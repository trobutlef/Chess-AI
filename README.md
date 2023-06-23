# Chess AI

  <div style="text-align:center">
  <img src="./static/img/chesspieces/wikipedia/bN.png"/>
   
  </div>

<a href="https://chess-ai-tony.herokuapp.com"> deployed by Heroku, Click here </a>

## Paper

Read my paper for my implemetation of this algorithm -> https://docs.google.com/document/d/1vdW18Gcsibg1j_nPxOuniDdTAz0CUVE7CLyWANVS7bQ/edit?usp=sharing

## Overview

Simple Chess Website built with flask, python-chess, chessboard.js, JQueryjs

## Usage

- Option #1
  - Use it on my website:
    https://chess-ai-tony.herokuapp.com
- Option #2 - Run it on the localhost
  - Clone Repository
  ```bash
  pip3 install python-chess tensorflow flask
  # then ...
  python3 app.py #running on port 4000
  ```
  - Install requirements.
  ```bash
  python3 -m pip install -r requirements.txt
  ```

## TODOs

- [ ] Add table UI with CSS
- [ ] Fix Legal moves UI
- [x] Solve problem with chessboard.js to display board on website
- [ ] Allow user to get new game server
- [ ] Allow user to take back one move
- [ ] Make model with Tensorflow and train with Stockfish training data

## Implementation

- Establish the search tree
- Use a neural net to prune the search tree

Definition : Value network
V - f(state)

State(Board):

Pieces(1-6 _ 2 - 13):
_ Blank
_ Pawn
_ Bishop
_ Knight
_ Rook
_ Queen
_ King

Extra state:
_ Castle available x2
_ En passant available x2

    8x8x4 - 4 = 260 bits

## Algorithms

### Minimax Algorithm

### Alpha-Beta Pruning

## Training Set

1. AI (white) vs Stockfish (Black)
2. AI (white) vs AI (Black)
3. AI (white) vs Human (Black)

## Steps to make a chess AI

1. Gather data: The AI needs to learn about the rules of chess and the possible moves that can be made.
2. Some algorithms: MINIMAX, Alpha-beta pruning, Monte Carlo Tree Search.
