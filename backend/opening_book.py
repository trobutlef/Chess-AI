# backend/opening_book.py
import os
import chess
import chess.pgn
from collections import defaultdict

# The opening_book dictionary:
#   Key: FEN string
#   Value: dict mapping move UCI strings to counts
opening_book = defaultdict(lambda: defaultdict(int))

def load_opening_book(data_folder="data", max_moves=10):
    """
    Reads PGN files from the provided folder and builds an opening book.
    Only the first `max_moves` of each game are recorded.
    """
    if not os.path.exists(data_folder):
        print(f"Data folder '{data_folder}' not found. No PGN training data loaded.")
        return
    
    for filename in os.listdir(data_folder):
        if filename.endswith(".pgn"):
            path = os.path.join(data_folder, filename)
            print(f"Loading PGN file: {path}")
            with open(path, encoding="utf-8") as pgn_file:
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
    print("Finished loading opening book.")

def get_trained_move(board):
    """
    Looks up the current board position in the opening book.
    Returns the move with the highest frequency if available.
    """
    fen = board.fen()
    if fen in opening_book:
        moves = opening_book[fen]
        best_move_uci = max(moves, key=moves.get)
        return chess.Move.from_uci(best_move_uci)
    return None
