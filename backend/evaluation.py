"""
Advanced positional evaluation for chess.
Includes piece-square tables, king safety, pawn structure, and mobility.
"""
import chess

# Piece base values (centipawns)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

# Piece-Square Tables (from White's perspective, a1=0)
# Values are in centipawns, positive = good for piece placement
# fmt: off
PAWN_TABLE = [
     0,   0,   0,   0,   0,   0,   0,   0,
    50,  50,  50,  50,  50,  50,  50,  50,
    10,  10,  20,  30,  30,  20,  10,  10,
     5,   5,  10,  25,  25,  10,   5,   5,
     0,   0,   0,  20,  20,   0,   0,   0,
     5,  -5, -10,   0,   0, -10,  -5,   5,
     5,  10,  10, -20, -20,  10,  10,   5,
     0,   0,   0,   0,   0,   0,   0,   0,
]

KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

ROOK_TABLE = [
     0,   0,   0,   0,   0,   0,   0,   0,
     5,  10,  10,  10,  10,  10,  10,   5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
     0,   0,   0,   5,   5,   0,   0,   0,
]

QUEEN_TABLE = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,   5,   5,   5,   0, -10,
     -5,   0,   5,   5,   5,   5,   0,  -5,
      0,   0,   5,   5,   5,   5,   0,  -5,
    -10,   5,   5,   5,   5,   5,   0, -10,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20,
]

KING_MIDDLEGAME_TABLE = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
     20,  20,   0,   0,   0,   0,  20,  20,
     20,  30,  10,   0,   0,  10,  30,  20,
]

KING_ENDGAME_TABLE = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10,   0,   0, -10, -20, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -30,   0,   0,   0,   0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50,
]
# fmt: on

PST = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
}


def get_pst_value(piece_type, square, is_white, is_endgame=False):
    """Get piece-square table value for a piece at a square."""
    if piece_type == chess.KING:
        table = KING_ENDGAME_TABLE if is_endgame else KING_MIDDLEGAME_TABLE
    else:
        table = PST.get(piece_type)
        if table is None:
            return 0
    
    # Mirror for black pieces (board is from white's perspective)
    if is_white:
        return table[63 - square]  # Flip vertically for white
    else:
        return table[square]


def is_endgame(board):
    """Determine if position is an endgame based on material."""
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
    minors = (
        len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK)) +
        len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.BLACK))
    )
    rooks = len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.BLACK))
    
    # Endgame if no queens or minimal material
    return queens == 0 or (queens <= 2 and minors + rooks <= 2)


def evaluate_material(board):
    """Evaluate material balance."""
    score = 0
    for piece_type in PIECE_VALUES:
        white_count = len(board.pieces(piece_type, chess.WHITE))
        black_count = len(board.pieces(piece_type, chess.BLACK))
        score += (white_count - black_count) * PIECE_VALUES[piece_type]
    return score


def evaluate_pst(board, endgame):
    """Evaluate piece placement using piece-square tables."""
    score = 0
    for square, piece in board.piece_map().items():
        value = get_pst_value(piece.piece_type, square, piece.color, endgame)
        if piece.color == chess.WHITE:
            score += value
        else:
            score -= value
    return score


def evaluate_pawn_structure(board):
    """Evaluate pawn structure: doubled, isolated, and passed pawns."""
    score = 0
    
    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        sign = 1 if color == chess.WHITE else -1
        
        # Count pawns per file
        files = [0] * 8
        for sq in pawns:
            files[chess.square_file(sq)] += 1
        
        for sq in pawns:
            file = chess.square_file(sq)
            rank = chess.square_rank(sq)
            
            # Doubled pawns penalty
            if files[file] > 1:
                score -= sign * 10
            
            # Isolated pawn penalty
            has_neighbor = False
            if file > 0 and files[file - 1] > 0:
                has_neighbor = True
            if file < 7 and files[file + 1] > 0:
                has_neighbor = True
            if not has_neighbor:
                score -= sign * 20
            
            # Passed pawn bonus
            is_passed = True
            enemy_pawns = board.pieces(chess.PAWN, not color)
            for enemy_sq in enemy_pawns:
                enemy_file = chess.square_file(enemy_sq)
                enemy_rank = chess.square_rank(enemy_sq)
                if abs(enemy_file - file) <= 1:
                    if color == chess.WHITE and enemy_rank > rank:
                        is_passed = False
                        break
                    elif color == chess.BLACK and enemy_rank < rank:
                        is_passed = False
                        break
            
            if is_passed:
                # Bonus increases as pawn advances
                advance = rank if color == chess.WHITE else (7 - rank)
                score += sign * (10 + advance * 10)
    
    return score


def evaluate_king_safety(board, endgame):
    """Evaluate king safety based on pawn shield."""
    if endgame:
        return 0  # King safety less important in endgame
    
    score = 0
    
    for color in [chess.WHITE, chess.BLACK]:
        king_sq = board.king(color)
        if king_sq is None:
            continue
            
        sign = 1 if color == chess.WHITE else -1
        king_file = chess.square_file(king_sq)
        king_rank = chess.square_rank(king_sq)
        
        # Pawn shield bonus
        shield_squares = []
        pawn_direction = 1 if color == chess.WHITE else -1
        
        for f in range(max(0, king_file - 1), min(8, king_file + 2)):
            shield_rank = king_rank + pawn_direction
            if 0 <= shield_rank <= 7:
                shield_squares.append(chess.square(f, shield_rank))
        
        pawns = board.pieces(chess.PAWN, color)
        for sq in shield_squares:
            if sq in pawns:
                score += sign * 10
    
    return score


def evaluate_mobility(board):
    """Evaluate piece mobility (number of legal moves)."""
    # This is expensive, so we use a simple approximation
    # Count attacked squares instead of full legal move generation
    score = 0
    
    # Simple mobility: count pieces that aren't on edge squares
    for color in [chess.WHITE, chess.BLACK]:
        sign = 1 if color == chess.WHITE else -1
        
        for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            for sq in board.pieces(piece_type, color):
                file = chess.square_file(sq)
                rank = chess.square_rank(sq)
                
                # Central squares give mobility bonus
                if 2 <= file <= 5 and 2 <= rank <= 5:
                    score += sign * 5
    
    return score


def evaluate_bishop_pair(board):
    """Bonus for having the bishop pair."""
    score = 0
    
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += 30
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= 30
    
    return score


def evaluate_board(board):
    """
    Complete positional evaluation.
    Returns score in centipawns from White's perspective.
    Positive = White is better, Negative = Black is better.
    """
    # Check for checkmate/stalemate
    if board.is_checkmate():
        return -10000 if board.turn == chess.WHITE else 10000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    
    endgame = is_endgame(board)
    
    score = 0
    score += evaluate_material(board)
    score += evaluate_pst(board, endgame)
    score += evaluate_pawn_structure(board)
    score += evaluate_king_safety(board, endgame)
    score += evaluate_mobility(board)
    score += evaluate_bishop_pair(board)
    
    # Convert to simple units (divide by 100 to match old interface)
    return score / 100.0
