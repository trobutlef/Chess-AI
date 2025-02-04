# opening_book.py
import os
import chess
import chess.pgn
import pickle
from collections import defaultdict

def train_opening_book(data_folder="data", max_moves=10):
    """
    Reads PGN files from the specified folder and builds an opening book.
    Returns a dictionary where:
      - Keys: FEN strings
      - Values: dictionaries mapping move UCI strings to occurrence counts.
    Only the first `max_moves` of each game are recorded.
    """
    opening_book = defaultdict(lambda: defaultdict(int))
    
    if not os.path.exists(data_folder):
        print(f"Data folder '{data_folder}' not found. No PGN training data loaded.")
        return dict(opening_book)
    
    for filename in os.listdir(data_folder):
        if filename.endswith(".pgn"):
            path = os.path.join(data_folder, filename)
            print(f"Training from PGN file: {path}")
            # Use errors="replace" to handle possible Unicode issues
            with open(path, encoding="utf-8", errors="replace") as pgn_file:
                while True:
                    game = chess.pgn.read_game(pgn_file)
                    if game is None:
                        break
                    board = game.board()
                    move_count = 0
                    for move in game.mainline_moves():
                        fen = board.fen()
                        opening_book[fen][move.uci()] += 1
                        board.push(move)
                        move_count += 1
                        if move_count >= max_moves:
                            break
    return dict(opening_book)

def save_opening_book(model, filename="opening_book_model.pkl"):
    """
    Saves the trained opening book model to a file using pickle.
    """
    with open(filename, "wb") as f:
        pickle.dump(model, f)
    print(f"Opening book model saved to {filename}")

def load_opening_book_model(filename="opening_book_model.pkl"):
    """
    Loads a pre-trained opening book model from disk.
    Returns the model (a dictionary) or None if the file does not exist.
    """
    if not os.path.exists(filename):
        print(f"Model file '{filename}' not found.")
        return None
    with open(filename, "rb") as f:
        model = pickle.load(f)
    return model

def get_trained_move(board, model):
    """
    Given a chess.Board and a pre-trained opening book model,
    returns the move (as a chess.Move) with the highest frequency if found.
    """
    if model is None:
        return None
    fen = board.fen()
    if fen in model:
        moves = model[fen]
        best_move_uci = max(moves, key=moves.get)
        return chess.Move.from_uci(best_move_uci)
    return None
