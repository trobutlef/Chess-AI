#!/usr/bin/env python3
import chess

class State(object):
    def __init__(self):
        self.board = chess.Board()

    def serialize(self):
        # 257 bits according to readme
        pass

    def edges(self):
        return list(self.board.legal_moves)

    def value(self):
        # TODO: add neural net here
        return 1 

if __name__ == "__main__":
    s = State()
    print(s.edges())
    print(s.value())
