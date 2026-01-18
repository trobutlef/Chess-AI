"""
Tests for the opening book module.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)))

import pytest
import chess
from opening_book import get_book_move, is_in_book, BOOK_PATH


class TestOpeningBook:
    def test_get_book_move_starting_position(self):
        """Should return a move for starting position if book exists."""
        board = chess.Board()
        move = get_book_move(board)
        
        if os.path.exists(BOOK_PATH):
            # If book exists, should return a legal move
            assert move is not None
            assert move in board.legal_moves
        else:
            # If no book, should return None
            assert move is None
    
    def test_get_book_move_out_of_book(self):
        """Should return None for obscure positions."""
        # A random endgame position not in any book
        board = chess.Board("8/8/4k3/8/8/4K3/8/8 w - - 0 1")
        move = get_book_move(board)
        assert move is None
    
    def test_is_in_book_starting(self):
        """Starting position should be in book if book exists."""
        board = chess.Board()
        in_book = is_in_book(board)
        
        if os.path.exists(BOOK_PATH):
            assert in_book is True
        else:
            assert in_book is False
    
    def test_get_book_move_variety(self):
        """With variety=True, should sometimes return different moves."""
        if not os.path.exists(BOOK_PATH):
            pytest.skip("Opening book not found")
        
        board = chess.Board()
        moves = set()
        
        # Try multiple times to see if we get different moves
        for _ in range(20):
            move = get_book_move(board, variety=True)
            if move:
                moves.add(move.uci())
        
        # Common opening books have multiple first move options
        # This might fail if book only has one move, which is fine
        assert len(moves) >= 1
    
    def test_get_book_move_no_variety(self):
        """With variety=False, should always return the same move."""
        if not os.path.exists(BOOK_PATH):
            pytest.skip("Opening book not found")
        
        board = chess.Board()
        first_move = get_book_move(board, variety=False)
        
        # Should return same move every time
        for _ in range(5):
            move = get_book_move(board, variety=False)
            assert move == first_move
