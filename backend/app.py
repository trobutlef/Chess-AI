#!usr/bin/env python3
from flask import Flask, render_template, jsonify, request
from backend.engine import Engine
import json
import chess

app = Flask(__name__)

engine = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/newgame')
def new_game():
    global engine
    engine = Engine()
    return jsonify(engine.board.fen())

@app.route('/bestmove', methods=['POST'])
def best_move():
    global engine
    move_data = json.loads(request.data)
    move_uci = move_data['move']
    move = chess.Move.from_uci(move_uci)
    if move in engine.board.legal_moves:
        engine.board.push(move)
    best_move = engine.get_best_move()
    if best_move:
        engine.board.push(best_move)
    return jsonify({'fen': engine.board.fen()})


if __name__ == '__main__':
    app.run(debug=True)
