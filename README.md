# Chess AI
  
  * Establish the search tree
  * Use a neural net to prune the search tree

  Definition : Value network
  V - f(state)

  State(Board):

  Pieces(1-6 * 2 - 13):
    * Blank
    * Pawn
    * Bishop
    * Knight 
    * Rook
    * Queen
    * King

  Extra state:
    * Castle available x2
    * En passant available x2

    8x8x4 - 4 = 260 bits
