import React, { useState, useEffect } from "react";
import axios from "axios";

const ChessBoard = () => {
  const [fen, setFen] = useState("");
  const [move, setMove] = useState("");

  useEffect(() => {
    // Start a new game on component mount
    const newGame = async () => {
      const response = await axios.get("/newgame");
      setFen(response.data);
    };
    newGame();
  }, []);

  const handleMove = async () => {
    try {
      const response = await axios.post("/bestmove", { move });
      setFen(response.data.fen);
    } catch (error) {
      console.error("Error making move:", error);
    }
  };

  return (
    <div>
      <div>Current FEN: {fen}</div>
      <input
        type="text"
        value={move}
        onChange={(e) => setMove(e.target.value)}
        placeholder="Enter your move in UCI format"
      />
      <button onClick={handleMove}>Make Move</button>
    </div>
  );
};

export default ChessBoard;
