# Chess AI

  <div style="text-align:center">
  <img src="./static/img/chesspieces/wikipedia/bN.png"/>
  </div>

## Paper
  Read my paper for my implemetation of this algorithm -> https://docs.google.com/document/d/1vdW18Gcsibg1j_nPxOuniDdTAz0CUVE7CLyWANVS7bQ/edit?usp=sharing


## Overview
  Simple Chess Website built with flask, python-chess, chessboard.js

## Features
  * 

## Usage
  * Option #1
    * Use it on our website:
      PUT LINK HERE...
  * Option #2 - Run it on the localhost
    * Clone Repository
    ```bash
    pip3 install python-chess tensorflow flask
    # then ...
    python3 app.py # might have to change the port from 4000 to 5000
    ```
    * Install requirements.
    ```bash
    python3 -m pip install -r requirements.txt
    ```
    
  

## TODOs
  - [ ] Add table UI with CSS
  - [ ] Solve problem with chessboard.js to display board on website
  - [ ] Allow user to get new game server
  - [ ] Allow user to take back one move
  - [ ] Make model with Tensorflow and train with Stockfish training data 

## Implementation
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

## Training Set
  1. AI (white) vs Stockfish (Black)
  2. AI (white) vs AI (Black)
  3. AI (white) vs Human (Black)
