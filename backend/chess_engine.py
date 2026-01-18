import math
import chess
from evaluation import evaluate_board

# Material values for MVV-LVA move ordering
VALUES = {
    chess.PAWN:   1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK:   5,
    chess.QUEEN:  9,
    chess.KING:   0,
}

_transposition_table = {}

def mvv_lva(move, board):
    """MVV-LVA ordering, safe for en passant."""
    if not board.is_capture(move):
        return 0

    # attacker always exists
    attacker = board.piece_at(move.from_square).piece_type

    # handle en passant specially
    if board.is_en_passant(move):
        victim_type = chess.PAWN
    else:
        victim_piece = board.piece_at(move.to_square)
        victim_type  = victim_piece.piece_type if victim_piece else chess.PAWN

    return VALUES[victim_type] - VALUES[attacker]

def quiescence(board, alpha, beta, is_maximizing):
    stand_pat = evaluate_board(board)
    if is_maximizing:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    # only capture moves
    caps = [m for m in board.legal_moves if board.is_capture(m)]
    caps.sort(key=lambda m: mvv_lva(m, board), reverse=True)
    for m in caps:
        board.push(m)
        val = -quiescence(board, -beta, -alpha, not is_maximizing)
        board.pop()
        if is_maximizing:
            alpha = max(alpha, val)
            if alpha >= beta: break
        else:
            beta = min(beta, val)
            if beta <= alpha: break

    return alpha if is_maximizing else beta

def minimax_alpha_beta(board, depth, alpha, beta, is_maximizing):
    key = (board.fen(), depth, is_maximizing)
    if key in _transposition_table:
        return _transposition_table[key]

    if depth == 0:
        val = quiescence(board, alpha, beta, is_maximizing)
        _transposition_table[key] = val
        return val

    moves = list(board.legal_moves)
    moves.sort(
        key=lambda m: (board.is_capture(m), mvv_lva(m, board)),
        reverse=True
    )

    best_val = -math.inf if is_maximizing else math.inf
    for m in moves:
        board.push(m)
        val = minimax_alpha_beta(board, depth - 1, alpha, beta, not is_maximizing)
        board.pop()

        if is_maximizing:
            best_val = max(best_val, val)
            alpha    = max(alpha, best_val)
            if alpha >= beta: break
        else:
            best_val = min(best_val, val)
            beta     = min(beta, best_val)
            if beta <= alpha: break

    _transposition_table[key] = best_val
    return best_val

def find_best_move(board, depth):
    is_white  = board.turn
    best_move = None
    best_val  = -math.inf if is_white else math.inf

    moves = list(board.legal_moves)
    moves.sort(key=lambda m: board.is_capture(m), reverse=True)

    for m in moves:
        board.push(m)
        val = minimax_alpha_beta(board, depth - 1, -math.inf, math.inf, not is_white)
        board.pop()
        if (is_white and val > best_val) or (not is_white and val < best_val):
            best_val  = val
            best_move = m

    return best_move
