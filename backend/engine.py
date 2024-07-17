import chess

class Engine():
    # constructor
    def __init__(self, fen=None):
      self.board = chess.Board(fen) if fen else chess.Board()
      self.MAX_DEPTH = 3
      self.piece_values = {
        chess.PAWN: 100,
        chess.BISHOP: 310,
        chess.KNIGHT: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 99999
      }

    def evaluate_board(self):
      """
      Basic board evaluation function. It just calculates the difference in piece values.
      """
      evaluation = 0
      for square in chess.SQUARES:
        piece = self.board.piece_at(square)
        if piece:
          value = self.piece_values[piece.piece_type]
          if piece.color == chess.WHITE:
            evaluation += value
          else:
            evaluation -= value
      return evaluation

    def alpha_beta(self, alpha, beta, depth):
        """
        Implementing the Alpha-Beta pruning algorithm.
        """
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board()

        if self.board.turn == chess.WHITE:
            max_eval = float('-inf')
            for move in self.board.legal_moves:
              self.board.push(move)
              eval = self.alpha_beta(alpha, beta, depth - 1)
              self.board.pop()
              max_eval = max(max_eval, eval)
              alpha = max(alpha, eval)
              if beta <= alpha:
                break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.board.legal_moves:
              self.board.push(move)
              eval = self.alpha_beta(alpha, beta, depth - 1)
              self.board.pop()
              min_eval = min(min_eval, eval)
              beta = min(beta, eval)
              if beta <= alpha:
                break
            return min_eval

    def get_best_move(self):
      """
      Returns the best move for the current board position.
      """
      best_move = None
      best_value = float('-inf') if self.board.turn == chess.WHITE else float('inf')

      for move in self.board.legal_moves:
        self.board.push(move)
        board_value = self.alpha_beta(float('-inf'), float('inf'), self.MAX_DEPTH - 1)
        self.board.pop()

        if self.board.turn == chess.WHITE and board_value > best_value:
          best_value = board_value
          best_move = move
        elif self.board.turn == chess.BLACK and board_value < best_value:
          best_value = board_value
          best_move = move

      return best_move


if __name__ == "__main__":
  new_engine = Engine()
  best_move = new_engine.get_best_move()
  print("Best Move:", best_move)
