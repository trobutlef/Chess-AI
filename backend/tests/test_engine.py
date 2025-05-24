import os, sys
# ensure backend/ is on PYTHONPATH
sys.path.insert(
    0,
    os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
)

import pytest
import chess
from chess_engine import find_best_move, evaluate_board

def test_minimax_returns_legal_move():
    """
    Ensure minimax at depth=1 always returns a legal move.
    """
    fen = "rnbqkbnr/pppp1ppp/8/4p3/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board = chess.Board(fen)
    move = find_best_move(board, depth=1)
    legal_uci = {m.uci() for m in board.legal_moves}
    assert move.uci() in legal_uci

# Integration tests for the API
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c

def test_api_minimax_start(client):
    res = client.post(
        "/api/chess/move",
        json={
            "fen":   "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "engine":"minimax", "depth":1
        }
    )
    assert res.status_code == 200
    assert "move" in res.get_json()

def test_api_neural_start(client):
    res = client.post(
        "/api/chess/move",
        json={"fen":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
              "engine":"neural"}
    )
    assert res.status_code == 200
    assert "move" in res.get_json()
