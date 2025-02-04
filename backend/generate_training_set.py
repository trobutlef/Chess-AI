#!/usr/bin/env python3
import os
import chess
import chess.pgn
import numpy as np

def serialize_board(board):
    """
    Converts the board to a flat array of 64 integers.
    Mapping:
      - Empty square: 0
      - White pieces: Pawn=1, Knight=2, Bishop=3, Rook=4, Queen=5, King=6
      - Black pieces: Pawn=-1, Knight=-2, Bishop=-3, Rook=-4, Queen=-5, King=-6
    """
    mapping = {None: 0}
    mapping.update({
        (chess.PAWN, True): 1,   (chess.PAWN, False): -1,
        (chess.KNIGHT, True): 2, (chess.KNIGHT, False): -2,
        (chess.BISHOP, True): 3, (chess.BISHOP, False): -3,
        (chess.ROOK, True): 4,   (chess.ROOK, False): -4,
        (chess.QUEEN, True): 5,  (chess.QUEEN, False): -5,
        (chess.KING, True): 6,   (chess.KING, False): -6,
    })
    board_array = []
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        board_array.append(mapping[piece] if piece is not None else 0)
    return np.array(board_array, dtype=np.int8)

def get_dataset(num_samples=None):
    """
    Iterates over all PGN files in the data folder to generate training examples.
    For each game, after each move the board is serialized. The label is determined by the game result:
      - '1-0'  --> +1 (win for White)
      - '0-1'  --> -1 (win for Black)
      - '1/2-1/2' --> 0 (draw)
    """
    X, Y = [], []
    game_count = 0
    result_values = {'1-0': 1, '0-1': -1, '1/2-1/2': 0}
    data_folder = "data"
    
    for fn in os.listdir(data_folder):
        if not fn.endswith(".pgn"):
            continue
        path = os.path.join(data_folder, fn)
        with open(path, encoding="utf-8", errors="replace") as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break
                result = game.headers.get("Result", None)
                if result not in result_values:
                    continue
                label = result_values[result]
                board = game.board()
                for move in game.mainline_moves():
                    board.push(move)
                    serialized = serialize_board(board)
                    X.append(serialized)
                    Y.append(label)
                print(f"Parsed game {game_count}: total samples so far = {len(X)}")
                game_count += 1
                if num_samples is not None and len(X) >= num_samples:
                    return np.array(X), np.array(Y)
    return np.array(X), np.array(Y)

if __name__ == "__main__":
    # For example, generate up to 25 million samples (or fewer if not available)
    X, Y = get_dataset(num_samples=25000000)
    os.makedirs("processed", exist_ok=True)
    np.savez("processed/dataset_25M.npz", X, Y)
    print("Dataset saved. X shape:", X.shape, "Y shape:", Y.shape)
