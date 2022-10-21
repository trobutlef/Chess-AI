import chess
import chess.svg

board = chess.Board()

for i in board.legal_moves:
  print(i)

  board.push_san("e4")
  board.push_san("e5")

  print(board)
chess.svg.piece(chess.Piece.from_symbol("R"))  
