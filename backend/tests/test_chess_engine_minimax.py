import time
import pytest
import chess
from chess_engine import find_best_move

@pytest.mark.parametrize("fen,depth", [
    # Very sparse position: only kings on d1/d3. 4-ply is trivial here.
    ("8/8/8/8/8/8/3K4/3k4 w - - 0 1", 4),
    # Same tiny position but flip side to move
    ("8/8/8/8/8/8/3K4/3k4 b - - 0 1", 4),
])
def test_minimax_depth4_completes_quickly(fen, depth):
    """
    In a near-empty board, Minimax at depth=4 should finish in under 0.5s
    and always return a legal king move.
    """
    board = chess.Board(fen)

    start = time.time()
    mv    = find_best_move(board, depth)
    dur   = time.time() - start

    # It should pick a legal move
    assert mv in board.legal_moves

    # And run quickly (adjust threshold as needed)
    assert dur < 0.5, f"Minimax depth {depth} took too long: {dur:.2f}s"
