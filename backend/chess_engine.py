# chess_engine.py
import math
import chess

def evaluate_board(board):
    """
    A simple evaluation function based on material count.
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # King's value is not used here.
    }
    value = 0
    for piece in board.piece_map().values():
        if piece.color == chess.WHITE:
            value += piece_values[piece.piece_type]
        else:
            value -= piece_values[piece.piece_type]
    return value

def minimax_alpha_beta(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    if is_maximizing:
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax_alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax_alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth):
    """
    Iterates over legal moves and returns the best move (in UCI format)
    based on minimax search with alpha–beta pruning.
    """
    best_move = None
    best_value = -math.inf if board.turn == chess.WHITE else math.inf
    for move in board.legal_moves:
        board.push(move)
        board_value = minimax_alpha_beta(board, depth - 1, -math.inf, math.inf, not board.turn)
        board.pop()
        if board.turn == chess.WHITE:
            if board_value > best_value:
                best_value = board_value
                best_move = move
        else:
            if board_value < best_value:
                best_value = board_value
                best_move = move
    return best_move
