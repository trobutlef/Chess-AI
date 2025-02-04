# backend/model/data_preprocessing.py
import chess.pgn
import numpy as np
import pickle

# Global variables for move labels
move_labels_dict = {}
current_label_index = 0

def extract_features_labels(pgn_file_path, max_samples=10000):
    features = []
    labels = []
    global current_label_index, move_labels_dict
    # Specify the correct encoding and handle errors
    with open(pgn_file_path, 'r', encoding='latin-1', errors='replace') as pgn:
        game_count = 0
        while True:
            try:
                game = chess.pgn.read_game(pgn)
            except Exception as e:
                print(f"Error reading game: {e}")
                break
            if game is None or game_count >= max_samples:
                break
            board = game.board()
            for node in game.mainline():
                if node.move is not None:
                    board_tensor = board_to_tensor(board)
                    move_label = move_to_label(node.move)
                    features.append(board_tensor)
                    labels.append(move_label)
                    board.push(node.move)
            game_count += 1
    return np.array(features), np.array(labels)

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

def move_to_label(move):
    global current_label_index, move_labels_dict
    move_san = move.uci()
    if move_san not in move_labels_dict:
        move_labels_dict[move_san] = current_label_index
        current_label_index += 1
    return move_labels_dict[move_san]

def save_move_labels_dict(filename='move_labels_dict.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(move_labels_dict, f)
