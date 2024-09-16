// src/components/ChessGame.js
import React, { useState, useEffect } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard"; // Corrected import
import axios from "axios";

const ChessGame = () => {
  const [game, setGame] = useState(new Chess());
  const [fen, setFen] = useState("start");
  const [isGameOver, setIsGameOver] = useState(false);

  useEffect(() => {
    // Initialize a new game
    axios
      .get("http://localhost:5000/api/new_game")
      .then((response) => {
        setFen(response.data.fen);
        setGame(new Chess(response.data.fen));
      })
      .catch((error) => {
        console.error("Error initializing game:", error);
      });
  }, []);

  const onDrop = async (sourceSquare, targetSquare, piece) => {
    const move = {
      from: sourceSquare,
      to: targetSquare,
      promotion: "q", // always promote to a queen for simplicity
    };

    const gameCopy = new Chess(game.fen());
    const moveResult = gameCopy.move(move);

    if (moveResult === null) return false;

    setGame(gameCopy);
    setFen(gameCopy.fen());

    // Send the move to the backend and get the AI's move
    try {
      const response = await axios.post("http://localhost:5000/api/make_move", {
        fen: gameCopy.fen(),
        move: move.from + move.to + (move.promotion ? move.promotion : ""),
      });

      const newFen = response.data.fen;
      // const aiMove = response.data.ai_move; // Unused variable

      const gameOver = response.data.game_over;
      const result = response.data.result;

      gameCopy.load(newFen);
      setGame(gameCopy);
      setFen(newFen);
      setIsGameOver(gameOver);

      if (gameOver) {
        alert("Game Over. Result: " + (result || "Draw"));
      }
    } catch (error) {
      console.error("Error making move:", error);
    }

    return true;
  };

  return (
    <div>
      <h1>Chess Game</h1>
      <Chessboard
        position={fen}
        onPieceDrop={onDrop}
        arePiecesDraggable={!isGameOver}
        boardWidth={500}
      />
    </div>
  );
};

export default ChessGame;
