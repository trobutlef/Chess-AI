import chess
import chess.svg

class Engine():
   #constuctor
   def __init__(self, fen):
     self.board = chess.Board()
     self.MAX_DEPTH = 60
     self.piece_values = {
      #pawn
      1:100,
      #bishop
      2:310,
      #knight
      3:300,
      # rook
      4:500,
      #queen
      5:900,
      #king
      6:99999
     }

if __name__ == "__main__":
  new_engine = Engine()
  print("hello")
