# Chess AI
  Simple Chess game with Machine Learning system

## Paper
  Read my paper for my implemetation of this algorithm -> https://docs.google.com/document/d/1vdW18Gcsibg1j_nPxOuniDdTAz0CUVE7CLyWANVS7bQ/edit?usp=sharing

## Features
  * 

## Usage
  ```bash
  pip3 install python-chess tensorflow flask
  # then ...
  python3 app.py # might have to change the port from 4000 to 5000
  ```

## TODOs
  - [ ] Finishing the 

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
  ---
