# Chess AI

A full-stack Chess AI application with two engines and a React frontend.

![Chess AI Screenshot](image.png)

## Features

- **Two AI Engines**:
  - **Minimax**: Alpha-beta pruning with quiescence search and transposition tables
  - **Neural Network**: CNN-based position evaluation using trained model
- **Advanced Evaluation**: Piece-square tables, pawn structure, king safety, mobility
- **Game History**: Save and review past games with PGN export
- **Chess Clock**: Time controls (bullet, blitz, rapid, unlimited)
- **Opening Book Support**: Polyglot format (optional)
- **Multiplayer**: WebSocket-based online play (optional)
- **Authentication**: Email/password and Google OAuth2
- **Mobile Responsive**: Works on phones and tablets

## Repository Structure

```
backend/
  app.py                   Flask API and game endpoints
  chess_engine.py          Minimax with alpha-beta pruning
  evaluation.py            Advanced positional evaluation
  neural_model.py          CNN architecture
  opening_book.py          Polyglot book support
  multiplayer.py           WebSocket multiplayer
  train_model.py           Neural network training
  tests/                   pytest test suite

frontend/
  src/
    App.js                 Main app with routing
    ChessGame.js           Game component with clock integration
    components/
      ChessClock.js        Chess timer component
      GameHistory.js       Past games list
      GameReview.js        Step through games
      Lobby.js             Multiplayer lobby
```

## Quick Start

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

API runs at `http://localhost:5001/`

### Frontend

```bash
cd frontend
npm install
npm start
```

App runs at `http://localhost:3000/`

## Configuration

Create `backend/.env`:

```
FLASK_SECRET_KEY=<your secret>
GOOGLE_OAUTH_CLIENT_ID=<client id>
GOOGLE_OAUTH_CLIENT_SECRET=<client secret>
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chess/move` | POST | Get AI move for position |
| `/api/games` | GET/POST | List/create games |
| `/api/games/<id>` | GET/DELETE | Get/delete game |
| `/api/games/<id>/move` | POST | Add move to game |
| `/api/login` | POST | Email/password login |
| `/api/register` | POST | Create account |
| `/api/logout` | POST | End session |
| `/api/me` | GET | Get current user |

### Chess Move Request

```json
{
  "fen": "<FEN string>",
  "depth": 3,
  "engine": "minimax" | "neural",
  "use_book": true
}
```

## Training the Neural Network

1. Place PGN files in `backend/data/`
2. Generate dataset:
   ```bash
   python generate_training_set.py
   ```
3. Train model:
   ```bash
   python train_model.py
   ```

Weights saved to `nets/value.pth`

## Running Tests

```bash
cd backend
pytest -v
```

## Notes

- Minimax depth 3-4 takes 2-10+ seconds per move
- Neural network is faster but requires training
- Opening book speeds up early game (download `.bin` file to `books/`)
- For production: use Gunicorn and set `FLASK_ENV=production`
