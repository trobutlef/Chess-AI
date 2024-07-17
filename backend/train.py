#!usr/bin/env python3
import os
import chess.pgn
import torch
import torch.nn as nn
import torch.optim as optim


class ChessModel(nn.Module):
  def __init__(self):
    super(ChessModel, self).__init__()
  def forward(self, x):
    pass

def load_data():
  inputs = []
  labels = []
  
  #print(os.listdir())
  for fn in os.listdir("data"):
    pgn = open(os.path.join("data", fn))
    while 1:
      try:
        game = chess.pgn.read_game(pgn)
        if game is None:
          break
        board = game.board()
        for move in game.mainline_moves():
          inputs.append(board.fen())
          board.push(move)
          labels.append(board.fen())
      except Exception:
        print(f"Error processing {fn}: {e}")
        break
      
      # result = game.headers['Result']
      # board = game.board()
      # for i, move in enumerate(game.mainline_moves()):
      #   board.push(move)
      #   print(i)
      #   print(result)
      #   print(board)
      # exit(0)
  return inputs, labels


