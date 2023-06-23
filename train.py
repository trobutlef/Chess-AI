#!usr/bin/env python3
import os
import chess.pgn


#print(os.listdir())
for fn in os.listdir("data"):
  pgn = open(os.path.join("data", fn))
  while 1:
    try:
      game = chess.pgn.read_game(pgn)
    except Exception:
      break
    

    result = game.headers['Result']
    board = game.board()
    for i, move in enumerate(game.mainline_moves()):
      board.push(move)
      print(i)
      print(result)
      print(board)

    break
