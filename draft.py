import chess
import random
import numpy

def create_random_board(max_depth=200):
    board = chess.Board()
    depth = random.randrange(0, max_depth)
    
    for i in range(depth):
        all_moves = list(board.legal_moves)
        random_move = random.choice(all_moves)
        board.push(random_move)
        if board.is_game_over():
            break
        
    return board

board = create_random_board()
print(board)