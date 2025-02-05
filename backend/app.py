# app.py
from dotenv import load_dotenv
load_dotenv()

import os
import chess
import torch
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_dance.contrib.google import make_google_blueprint, google
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Import our search engine and neural network modules
from chess_engine import find_best_move
from neural_model import load_model, serialize_board

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
CORS(app, supports_credentials=True)

# Configure SQLAlchemy (using SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ------------------ User Model ---------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(150))
    password = db.Column(db.String(255), nullable=True)  # For email/password users; null for OAuth

# ------------------ Google OAuth Setup ---------------------
#print(os.environ.get("GOOGLE_OAUTH_CLIENT_ID"))
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
#print(os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"))
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
google_bp = make_google_blueprint(
    scope=["profile", "email"],
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# ------------------ Global Neural Model Loading ---------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
# Load the pre-trained neural network model.
# (Ensure that you have already trained the network and saved the weights to nets/value.pth.)
neural_model = load_model("nets/value.pth", device=device)

# ------------------ API Endpoints ---------------------
@app.route("/")
def index():
    return "Welcome to Chess AI API"

@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_info = resp.json()
        email = user_info["email"]
        name = user_info.get("name", email)
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name=name)
            db.session.add(user)
            db.session.commit()
        session["user_id"] = user.id
        return redirect("http://localhost:3000/")
    return "Failed to fetch user info", 400

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    app.logger.info("Registration data: %s", data)
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    email = data.get("email")
    password = data.get("password")
    name = data.get("name", email)
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(email=email, name=name, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        app.logger.info("User %s registered successfully.", email)
        return jsonify({"message": "User registered successfully"})
    except Exception as e:
        app.logger.error("Registration error: %s", e)
        return jsonify({"error": "Registration failed"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    app.logger.info("Login data: %s", data)
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.password:
        return jsonify({"error": "User not found or password not set"}), 400

    if bcrypt.check_password_hash(user.password, password):
        session["user_id"] = user.id
        app.logger.info("User %s logged in successfully.", email)
        return jsonify({"message": "Logged in successfully"})
    else:
        return jsonify({"error": "Invalid credentials"}), 400

@app.route("/api/chess/move", methods=["POST"])
def chess_move():
    """
    Expects JSON data:
    {
      "fen": "<FEN string>",
      "depth": <int, optional>,  # for minimax search
      "engine": "minimax" or "neural"
    }
    Returns the best move in UCI notation.
    """
    data = request.get_json()
    fen = data.get("fen")
    depth = data.get("depth", 3)
    engine = data.get("engine", "minimax")
    
    try:
        board = chess.Board(fen)
    except Exception as e:
        return jsonify({"error": "Invalid FEN"}), 400

    if engine == "neural":
        # Use the neural network to select a move via a one-ply search.
        best_move = None
        best_eval = None
        # Determine which side is moving.
        moving_side = board.turn  # True for White, False for Black
        for move in board.legal_moves:
            board.push(move)
            # Serialize the board to a flat array and reshape to (1, 1, 8, 8).
            board_array = serialize_board(board)
            board_tensor = torch.tensor(board_array, dtype=torch.float32).view(1, 1, 8, 8).to(device)
            with torch.no_grad():
                value = neural_model(board_tensor).item()
            board.pop()
            # For White, we choose the move with the highest evaluation; for Black, the lowest.
            if moving_side == chess.WHITE:
                if best_eval is None or value > best_eval:
                    best_eval = value
                    best_move = move
            else:
                if best_eval is None or value < best_eval:
                    best_eval = value
                    best_move = move
        move = best_move
    else:
        # Use the minimax with alpha–beta pruning search.
        move = find_best_move(board, depth)

    if move:
        return jsonify({"move": move.uci()})
    else:
        return jsonify({"move": None, "error": "No valid move found"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
