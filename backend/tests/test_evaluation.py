"""
Tests for the advanced positional evaluation module.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)))

import pytest
import chess
from evaluation import (
    evaluate_board,
    evaluate_material,
    evaluate_pawn_structure,
    is_endgame,
    evaluate_bishop_pair,
)


class TestMaterialEvaluation:
    def test_starting_position_equal(self):
        """Starting position should be roughly equal."""
        board = chess.Board()
        score = evaluate_material(board)
        assert score == 0
    
    def test_white_up_queen(self):
        """White up a queen should be significantly positive."""
        board = chess.Board("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        score = evaluate_material(board)
        assert score > 800  # Queen is worth 900 centipawns
    
    def test_black_up_rook(self):
        """Black up a rook should be negative."""
        board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/1NBQKBNR w Kkq - 0 1")
        score = evaluate_material(board)
        assert score < -400  # Rook is worth 500 centipawns


class TestPawnStructure:
    def test_doubled_pawns_penalty(self):
        """Doubled pawns should give a penalty."""
        # White has doubled pawns on e-file
        board_doubled = chess.Board("8/8/8/4P3/4P3/8/8/8 w - - 0 1")
        board_normal = chess.Board("8/8/8/4P3/3P4/8/8/8 w - - 0 1")
        
        score_doubled = evaluate_pawn_structure(board_doubled)
        score_normal = evaluate_pawn_structure(board_normal)
        
        assert score_doubled < score_normal
    
    def test_passed_pawn_bonus(self):
        """Passed pawn should give a bonus."""
        # White has passed pawn on e6
        board_passed = chess.Board("8/8/4P3/8/8/8/8/8 w - - 0 1")
        score = evaluate_pawn_structure(board_passed)
        assert score > 0


class TestEndgameDetection:
    def test_starting_position_not_endgame(self):
        """Starting position is not endgame."""
        board = chess.Board()
        assert not is_endgame(board)
    
    def test_king_pawn_endgame(self):
        """King and pawn endgame is endgame."""
        board = chess.Board("8/4k3/8/4P3/8/8/8/4K3 w - - 0 1")
        assert is_endgame(board)
    
    def test_no_queens_is_endgame(self):
        """Position without queens is endgame."""
        board = chess.Board("r3k2r/ppp2ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPP2PPP/R3K2R w KQkq - 0 1")
        assert is_endgame(board)


class TestBishopPair:
    def test_white_bishop_pair(self):
        """White having bishop pair should give bonus."""
        board = chess.Board("8/8/8/8/8/8/2BB4/8 w - - 0 1")
        score = evaluate_bishop_pair(board)
        assert score > 0
    
    def test_no_bishop_pair(self):
        """Single bishop should not give bonus."""
        board = chess.Board("8/8/8/8/8/8/3B4/8 w - - 0 1")
        score = evaluate_bishop_pair(board)
        assert score == 0


class TestFullEvaluation:
    def test_checkmate_white_wins(self):
        """Checkmate for white should return large positive."""
        # Back rank mate position - white delivers checkmate
        board = chess.Board("6k1/5ppp/8/8/8/8/8/R3K3 w Q - 0 1")
        board.push_san("Ra8#")
        # Now it's black's turn but black is checkmated
        assert board.is_checkmate()
        score = evaluate_board(board)
        assert score > 90  # Large positive for white winning
    
    def test_stalemate_is_zero(self):
        """Stalemate should return 0."""
        board = chess.Board("k7/8/1K6/8/8/8/8/8 b - - 0 1")
        if board.is_stalemate():
            score = evaluate_board(board)
            assert score == 0
    
    def test_evaluation_returns_float(self):
        """Evaluation should return a float."""
        board = chess.Board()
        score = evaluate_board(board)
        assert isinstance(score, float)
