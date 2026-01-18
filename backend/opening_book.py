"""
Opening book support using Polyglot format.
Falls back to engine calculation when out of book.
"""
import os
import random
import chess
import chess.polyglot

# Path to the polyglot opening book
BOOK_PATH = os.path.join(os.path.dirname(__file__), "books", "performance.bin")


def get_book_move(board, variety=True):
    """
    Get a move from the opening book for the current position.
    
    Args:
        board: chess.Board - current position
        variety: bool - if True, choose weighted random; if False, choose best
    
    Returns:
        chess.Move or None if position not in book
    """
    if not os.path.exists(BOOK_PATH):
        return None
    
    try:
        with chess.polyglot.open_reader(BOOK_PATH) as reader:
            entries = list(reader.find_all(board))
            
            if not entries:
                return None
            
            if variety:
                # Weighted random selection based on weight
                total_weight = sum(e.weight for e in entries)
                if total_weight == 0:
                    return random.choice(entries).move
                
                r = random.randint(0, total_weight - 1)
                cumulative = 0
                for entry in entries:
                    cumulative += entry.weight
                    if r < cumulative:
                        return entry.move
                return entries[0].move
            else:
                # Return highest-weight move
                return max(entries, key=lambda e: e.weight).move
                
    except Exception:
        return None


def is_in_book(board):
    """Check if current position is in the opening book."""
    if not os.path.exists(BOOK_PATH):
        return False
    
    try:
        with chess.polyglot.open_reader(BOOK_PATH) as reader:
            return reader.get(board) is not None
    except Exception:
        return False
