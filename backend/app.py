from dotenv import load_dotenv
load_dotenv()

import os
import time
import logging

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

# --------------------
# App & Config
# --------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "supersekrit")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///db.sqlite3"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Set up SERVER_NAME so OAuth redirect URIs line up (host:port)
PORT = int(os.getenv("PORT", 5001))
app.config["SERVER_NAME"] = f"localhost:{PORT}"

# CORS
if os.getenv("FLASK_ENV") == "production":
    origins = os.getenv("CORS_ORIGINS", "").split(",")
    CORS(app, supports_credentials=True,
         resources={r"/api/*": {"origins": origins}})
else:
    CORS(app, supports_credentials=True)

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

@app.route("/api/me")
def me():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"user": None})
    user = User.query.get(uid)
    return jsonify({"user": {"email": user.email, "name": user.name}})

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

    try:
        board = chess.Board(fen)
    except Exception:
        return jsonify({"error": "Invalid FEN"}), 400

    start = time.time()
    try:
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
        "Engine=%s depth=%d fen=%s took %.2fs",
        engine, depth, fen, elapsed
    )

    if best_move is None:
        return jsonify({"error": "No valid move"}), 500

    return jsonify({"move": best_move.uci()})

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
