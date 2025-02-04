#!/usr/bin/env python3
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch import optim
import os

class ChessValueDataset(Dataset):
    def __init__(self):
        data = np.load("processed/dataset_25M.npz")
        self.X = data['arr_0']
        self.Y = data['arr_1']
        print("Loaded dataset: X shape =", self.X.shape, "Y shape =", self.Y.shape)

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        # Convert the flat board array (64,) into a tensor with shape (1, 8, 8)
        x = torch.tensor(self.X[idx], dtype=torch.float32).view(1, 8, 8)
        y = torch.tensor(self.Y[idx], dtype=torch.float32)
        return x, y

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # A simple CNN for 8x8 board input.
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)   # 16 x 8 x 8
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)  # 32 x 8 x 8
        self.pool = nn.MaxPool2d(2, 2)                            # 32 x 4 x 4
        self.fc1 = nn.Linear(32 * 4 * 4, 64)
        self.fc2 = nn.Linear(64, 1)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(-1, 32 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return torch.tanh(x)  # Output between -1 and 1

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dataset = ChessValueDataset()
    train_loader = DataLoader(dataset, batch_size=256, shuffle=True)
    model = Net().to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    model.train()
    os.makedirs("nets", exist_ok=True)
    for epoch in range(100):
        total_loss = 0.0
        for data, target in train_loader:
            data = data.to(device)
            target = target.to(device).unsqueeze(1)  # reshape target to (batch, 1)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1:03d}: Loss = {avg_loss:.6f}")
        torch.save(model.state_dict(), "nets/value.pth")
