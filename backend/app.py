# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import numpy as np
import pickle
import os
from tensorflow.keras.models import load_model
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from the frontend

# Secret key for session management (if needed)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# Initialize Firebase Admin SDK
cred = credentials.Certificate('path/to/serviceAccountKey.json')  # Update with the correct path
firebase_admin.initialize_app(cred)

# Load the trained model
model = load_model('model/chess_model.h5')

# Load the move labels dictionary
with open('model/move_labels_dict.pkl', 'rb') as f:
    move_labels_dict = pickle.load(f)

# Create reverse mapping from label to move SAN
label_to_move = {v: k for k, v in move_labels_dict.items()}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Firebase Authentication REST API
    try:
        import requests
        api_key = os.environ.get('FIREBASE_API_KEY', 'your_firebase_api_key')
        auth_url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}'
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        r = requests.post(auth_url, data=payload)
        if r.status_code == 200:
            user_info = r.json()
            id_token = user_info['idToken']
            return jsonify({'idToken': id_token}), 200
        else:
            return jsonify({'error': r.json()['error']['message']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        user = auth.create_user(email=email, password=password)
        return jsonify({'message': 'User created successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/new_game', methods=['GET'])
def new_game():
    board = chess.Board()
    fen = board.fen()
    return jsonify({'fen': fen})

@app.route('/api/make_move', methods=['POST'])
def make_move():
    data = request.json
    fen = data.get('fen')
    move_uci = data.get('move')

    board = chess.Board(fen)

    # Human move
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
        else:
            return jsonify({'error': 'Invalid move'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid move format'}), 400

    # AI move
    if not board.is_game_over():
        ai_move = get_ai_move(board)
        board.push(ai_move)
        ai_move_san = ai_move.uci()
    else:
        ai_move_san = None

    new_fen = board.fen()
    game_over = board.is_game_over()
    result = board.result() if game_over else None

    return jsonify({
        'fen': new_fen,
        'ai_move': ai_move_san,
        'game_over': game_over,
        'result': result
    })

def get_ai_move(board):
    input_tensor = board_to_tensor(board)
    input_tensor = np.expand_dims(input_tensor, axis=0)
    move_probs = model.predict(input_tensor)[0]

    legal_moves = list(board.legal_moves)
    legal_move_indices = []
    for move in legal_moves:
        move_san = move.uci()
        move_index = move_labels_dict.get(move_san)
        if move_index is not None:
            legal_move_indices.append((move_index, move))

    if not legal_move_indices:
        return random.choice(legal_moves)

    # Get probabilities for legal moves
    legal_move_probs = [(move_probs[index], move) for index, move in legal_move_indices]

    # Choose the move with the highest probability
    best_move = max(legal_move_probs, key=lambda x: x[0])[1]

    return best_move

def board_to_tensor(board):
    tensor = np.zeros((8, 8, 12), dtype=np.int8)
    piece_to_index = {
        chess.Piece(chess.PAWN, chess.WHITE): 0,
        chess.Piece(chess.KNIGHT, chess.WHITE): 1,
        chess.Piece(chess.BISHOP, chess.WHITE): 2,
        chess.Piece(chess.ROOK, chess.WHITE): 3,
        chess.Piece(chess.QUEEN, chess.WHITE): 4,
        chess.Piece(chess.KING, chess.WHITE): 5,
        chess.Piece(chess.PAWN, chess.BLACK): 6,
        chess.Piece(chess.KNIGHT, chess.BLACK): 7,
        chess.Piece(chess.BISHOP, chess.BLACK): 8,
        chess.Piece(chess.ROOK, chess.BLACK): 9,
        chess.Piece(chess.QUEEN, chess.BLACK): 10,
        chess.Piece(chess.KING, chess.BLACK): 11,
    }
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_index = piece_to_index[piece]
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            tensor[row, col, piece_index] = 1
    return tensor

if __name__ == '__main__':
    app.run(debug=True)
