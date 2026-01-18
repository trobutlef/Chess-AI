from dotenv import load_dotenv
load_dotenv()

import os
import time
import logging
from datetime import datetime

import chess
import numpy as np
import torch
from flask import (
    Flask, redirect, url_for,
    session, request, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_dance.contrib.google import make_google_blueprint, google

from chess_engine import find_best_move
from neural_model import load_model, serialize_board
from opening_book import get_book_move

# --------------------
# App & Config
# --------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "supersekrit")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///db.sqlite3"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Set up SERVER_NAME only in production (causes issues in dev)
PORT = int(os.getenv("PORT", 5001))
if os.getenv("FLASK_ENV") == "production":
    app.config["SERVER_NAME"] = os.getenv("SERVER_NAME", f"localhost:{PORT}")

# CORS - must specify explicit origins when using credentials
CORS(app, 
     resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}},
     supports_credentials=True)

# --------------------
# Logging
# --------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------
# Database + Migrations
# --------------------
db      = SQLAlchemy(app)
bcrypt  = Bcrypt(app)
migrate = Migrate(app, db)

# --------------------
# Models
# --------------------
class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(150), unique=True)
    name     = db.Column(db.String(150))
    password = db.Column(db.String(255), nullable=True)
    games    = db.relationship('Game', backref='user', lazy=True)


class Game(db.Model):
    """Stores game history for users."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    opponent_type = db.Column(db.String(20), default='ai')  # 'ai' or 'human'
    opponent_id = db.Column(db.Integer, nullable=True)  # For multiplayer
    engine = db.Column(db.String(20), default='minimax')  # 'minimax' or 'neural'
    depth = db.Column(db.Integer, default=3)
    time_control = db.Column(db.Integer, nullable=True)  # Total time in seconds
    pgn = db.Column(db.Text, default='')  # Game moves in PGN format
    result = db.Column(db.String(10), default='*')  # '1-0', '0-1', '1/2-1/2', '*'
    user_color = db.Column(db.String(5), default='white')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    white_time = db.Column(db.Integer, nullable=True)  # Remaining time in ms
    black_time = db.Column(db.Integer, nullable=True)  # Remaining time in ms


# --------------------
# Google OAuth
# --------------------
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_REDIRECT = os.getenv(
    "GOOGLE_REDIRECT_URI",
    f"http://localhost:{PORT}/login/google/authorized"
)
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    redirect_url=GOOGLE_REDIRECT,
    redirect_to="handle_google_login",
)
app.register_blueprint(google_bp, url_prefix="/login")

@app.route("/login/google/success")
def handle_google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info", 400
    info  = resp.json()
    email = info["email"]
    name  = info.get("name", email)

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name)
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    return redirect(os.getenv("FRONTEND_URL", "http://localhost:3000"))

# --------------------
# Auth Endpoints
# --------------------
@app.route("/api/register", methods=["POST"])
def register():
    data  = request.get_json() or {}
    email = data.get("email")
    pwd   = data.get("password")
    name  = data.get("name", email)
    if not email or not pwd:
        return jsonify({"error": "Email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    hashed = bcrypt.generate_password_hash(pwd).decode()
    user   = User(email=email, name=name, password=hashed)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"})

@app.route("/api/login", methods=["POST"])
def login():
    data  = request.get_json() or {}
    email = data.get("email")
    pwd   = data.get("password")
    if not email or not pwd:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, pwd):
        return jsonify({"error": "Invalid credentials"}), 400

    session["user_id"] = user.id
    return jsonify({"message": "Logged in successfully"})

@app.route("/api/logout", methods=["POST"])
def logout():
    """Clear session and log user out."""
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@app.route("/api/me")
def me():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"user": None})
    user = User.query.get(uid)
    return jsonify({"user": {"email": user.email, "name": user.name}})

# --------------------
# Game History Endpoints
# --------------------
@app.route("/api/games", methods=["GET"])
def list_games():
    """Get all games for the current user."""
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "Not authenticated"}), 401
    
    games = Game.query.filter_by(user_id=uid).order_by(Game.created_at.desc()).all()
    return jsonify({
        "games": [{
            "id": g.id,
            "opponent_type": g.opponent_type,
            "engine": g.engine,
            "depth": g.depth,
            "result": g.result,
            "user_color": g.user_color,
            "time_control": g.time_control,
            "created_at": g.created_at.isoformat(),
            "pgn": g.pgn
        } for g in games]
    })

@app.route("/api/games", methods=["POST"])
def create_game():
    """Create a new game."""
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json() or {}
    game = Game(
        user_id=uid,
        opponent_type=data.get("opponent_type", "ai"),
        engine=data.get("engine", "minimax"),
        depth=data.get("depth", 3),
        time_control=data.get("time_control"),
        user_color=data.get("user_color", "white"),
        white_time=data.get("time_control", 0) * 1000 if data.get("time_control") else None,
        black_time=data.get("time_control", 0) * 1000 if data.get("time_control") else None,
    )
    db.session.add(game)
    db.session.commit()
    
    return jsonify({
        "id": game.id,
        "opponent_type": game.opponent_type,
        "engine": game.engine,
        "depth": game.depth,
        "time_control": game.time_control,
        "user_color": game.user_color,
        "white_time": game.white_time,
        "black_time": game.black_time,
    })

@app.route("/api/games/<int:game_id>", methods=["GET"])
def get_game(game_id):
    """Get a specific game."""
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "Not authenticated"}), 401
    
    game = Game.query.filter_by(id=game_id, user_id=uid).first()
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    return jsonify({
        "id": game.id,
        "opponent_type": game.opponent_type,
        "engine": game.engine,
        "depth": game.depth,
        "result": game.result,
        "user_color": game.user_color,
        "time_control": game.time_control,
        "pgn": game.pgn,
        "created_at": game.created_at.isoformat(),
        "white_time": game.white_time,
        "black_time": game.black_time,
    })

@app.route("/api/games/<int:game_id>/move", methods=["POST"])
def add_move(game_id):
    """Add a move to game history and update times."""
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "Not authenticated"}), 401
    
    game = Game.query.filter_by(id=game_id, user_id=uid).first()
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    data = request.get_json() or {}
    move_san = data.get("move")
    
    if move_san:
        # Append to PGN
        moves = game.pgn.split() if game.pgn else []
        move_number = len(moves) // 2 + 1
        if len(moves) % 2 == 0:
            game.pgn = f"{game.pgn} {move_number}. {move_san}".strip()
        else:
            game.pgn = f"{game.pgn} {move_san}".strip()
    
    # Update times if provided
    if "white_time" in data:
        game.white_time = data["white_time"]
    if "black_time" in data:
        game.black_time = data["black_time"]
    if "result" in data:
        game.result = data["result"]
    
    db.session.commit()
    return jsonify({"success": True, "pgn": game.pgn})

@app.route("/api/games/<int:game_id>", methods=["DELETE"])
def delete_game(game_id):
    """Delete a game."""
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "Not authenticated"}), 401
    
    game = Game.query.filter_by(id=game_id, user_id=uid).first()
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    db.session.delete(game)
    db.session.commit()
    return jsonify({"message": "Game deleted"})

# --------------------
# Load Neural Model
# --------------------
device       = "cuda" if torch.cuda.is_available() else "cpu"
model_path   = os.getenv("NEURAL_MODEL_PATH", "nets/value.pth")
neural_model = load_model(model_path, device=device)

# --------------------
# Chess Move Endpoint with timing
# --------------------
@app.route("/api/chess/move", methods=["POST"])
def chess_move():
    data   = request.get_json() or {}
    fen    = data.get("fen")
    depth  = data.get("depth", 3)
    engine = data.get("engine", "minimax")
    use_book = data.get("use_book", True)

    try:
        board = chess.Board(fen)
    except Exception:
        return jsonify({"error": "Invalid FEN"}), 400

    start = time.time()
    book_move_used = False
    
    try:
        # Try opening book first (for both engines)
        if use_book:
            book_move = get_book_move(board)
            if book_move:
                best_move = book_move
                book_move_used = True
                logger.info("Book move used: %s", book_move.uci())
        
        if not book_move_used:
            if engine == "minimax":
                best_move = find_best_move(board, depth)
            else:
                # Neural network path
                moves  = list(board.legal_moves)
                boards = []
                for m in moves:
                    board.push(m)
                    boards.append(serialize_board(board))
                    board.pop()
                arr    = np.stack(boards)
                tensor = torch.tensor(arr, dtype=torch.float32).view(-1,1,8,8).to(device)
                with torch.no_grad():
                    vals = neural_model(tensor).cpu().numpy().flatten()
                idx        = vals.argmax() if board.turn else vals.argmin()
                best_move  = moves[idx]
    except Exception as e:
        logger.error("Engine %s failed", engine, exc_info=e)
        return jsonify({"error": f"{engine} failed"}), 500

    elapsed = time.time() - start
    logger.info(
        "Engine=%s depth=%d fen=%s took %.2fs book=%s",
        engine, depth, fen, elapsed, book_move_used
    )

    if best_move is None:
        return jsonify({"error": "No valid move"}), 500

    return jsonify({
        "move": best_move.uci(),
        "from_book": book_move_used,
        "time_taken": round(elapsed, 3)
    })

# --------------------
# Main
# --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    logger.info("Starting Chess AI backend on 127.0.0.1:%s", PORT)
    app.run(
        host="127.0.0.1",
        port=PORT,
        debug=False,
        use_reloader=False,
    )
