# Chess AI Backend

This project implements a Chess AI that allows users to choose between two evaluation engines:

- **Minimax with Alpha-Beta Pruning** for classic search-based move selection.
- **Neural Network Model** trained on PGN files for position evaluation.

The backend is powered by **Flask**, and the AI models are built using **PyTorch**.

---

## Project Structure

```
backend/
├── app.py                    # Flask API for user interaction
├── chess_engine.py           # Minimax algorithm with alpha-beta pruning
├── neural_model.py           # Neural network architecture and utilities
├── generate_training_set.py  # Generates training data from PGN files
├── train_model.py            # Trains the neural network
├── data/                     # Folder for PGN files (not tracked in Git)
├── processed/                # Processed datasets (not tracked in Git)
├── nets/                     # Trained models (e.g., value.pth)
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables (not tracked in Git)
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- Pip
- [Git](https://git-scm.com/)

### Installation

Clone the repository:

```bash
git clone https://github.com/your-username/Chess-AI.git
cd Chess-AI/backend
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file to store sensitive information:

```ini
FLASK_SECRET_KEY=your_secret_key
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret
```

Ensure `.env` is ignored by Git:

```bash
echo ".env" >> .gitignore
```

---

## Usage

### Generate the Dataset

Place your PGN files inside the `data/` folder.

Run the following script to process the PGN files:

```bash
python generate_training_set.py
```

The dataset will be saved in the `processed/` folder.

---

### Train the Model

Train the neural network using:

```bash
python train_model.py
```

The trained model will be saved in the `nets/` folder as `value.pth`.

---

### Run the API

Start the Flask API:

```bash
python app.py
```

The API will be available at `http://localhost:5000/`.

---

## API Endpoints

### `POST /api/chess/move`

**Request:**

```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "depth": 3,
  "engine": "neural" // or "minimax"
}
```

**Response:**

```json
{
  "move": "e2e4"
}
```

---

## Authentication

Google OAuth is integrated for user authentication. Make sure to set the `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in your `.env` file.

---

## GitHub Large File Handling

To prevent large files from being pushed to GitHub:

1. Add directories to `.gitignore`:

```
# Ignore data, models, and environments
data/
processed/
nets/
venv/
.env
```

2. If large files were already committed:

```bash
git rm --cached path/to/largefile
git commit -m "Remove large file"
git push
```

For files >100 MB, consider using [Git LFS](https://git-lfs.github.com/).

---

## Tech Stack

- **Flask** - Web Framework
- **PyTorch** - Neural Network Library
- **python-chess** - Chess Engine Integration
- **SQLAlchemy** - Database ORM
- **OAuth with Google** - User Authentication

---

## Acknowledgments

Inspired by classic chess engines and modern AI-based approaches like AlphaZero.

---

## TODO

- Host the application on a free platform that supports Flask and SQLite for user registration and authentication. Potential options include **Render**, **Vercel**, or **Railway**.
