# neural_model.py
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import chess

def serialize_board(board):
    """
    Serializes the board to a flat numpy array of shape (64,) using the following mapping:
      - Empty square: 0
      - White pieces: Pawn=1, Knight=2, Bishop=3, Rook=4, Queen=5, King=6
      - Black pieces: Pawn=-1, Knight=-2, Bishop=-3, Rook=-4, Queen=-5, King=-6
    """
    mapping = {None: 0}
    mapping.update({
        (chess.PAWN, True): 1,   (chess.PAWN, False): -1,
        (chess.KNIGHT, True): 2, (chess.KNIGHT, False): -2,
        (chess.BISHOP, True): 3, (chess.BISHOP, False): -3,
        (chess.ROOK, True): 4,   (chess.ROOK, False): -4,
        (chess.QUEEN, True): 5,  (chess.QUEEN, False): -5,
        (chess.KING, True): 6,   (chess.KING, False): -6,
    })
    board_array = []
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            board_array.append(0)
        else:
            board_array.append(mapping[(piece.piece_type, piece.color)])
    return np.array(board_array, dtype=np.int8)

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # A simple CNN for an 8x8 board input.
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)  # Output: 16 x 8 x 8
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1) # Output: 32 x 8 x 8
        self.pool = nn.MaxPool2d(2,2)                           # Output: 32 x 4 x 4
        self.fc1 = nn.Linear(32 * 4 * 4, 64)
        self.fc2 = nn.Linear(64, 1)
        
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(-1, 32 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return torch.tanh(x)

def load_model(weights_path="nets/value.pth", device="cpu"):
    model = Net().to(device)
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()
    return model
