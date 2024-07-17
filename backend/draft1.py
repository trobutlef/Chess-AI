import os

image_path = "/static/img/chesspieces/wikipedia/"

# Verify if images exist
for piece in ['wN', 'wB', 'wQ', 'wK', 'wP', 'bR', 'bN', 'bB', 'bQ', 'bK', 'bP']:
    if not os.path.exists(f"{image_path}{piece}.png"):
        print(f"Image for {piece} not found!")
