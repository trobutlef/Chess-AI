// frontend/src/ChessBoard.js
import React, { useState } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";
import axios from "axios";
import { Box, Button, TextField, Typography, MenuItem } from "@mui/material";

function ChessBoardComponent() {
  // Initialize a chess.js game instance
  const [game, setGame] = useState(new Chess());
  const [fen, setFen] = useState(game.fen());
  const [bestMove, setBestMove] = useState("");
  const [depth, setDepth] = useState(3);
  const [engine, setEngine] = useState("minimax");

  // onPieceDrop validates moves and updates the game state.
  const onDrop = (sourceSquare, targetSquare) => {
    const move = game.move({
      from: sourceSquare,
      to: targetSquare,
      promotion: "q", // Always promote to queen for simplicity.
    });
    if (move === null) return false; // Illegal move
    setFen(game.fen());
    return true;
  };

  const handleGetMove = async () => {
    try {
      const response = await axios.post(
        "http://localhost:5000/api/chess/move",
        {
          fen: game.fen(),
          depth: depth,
          engine: engine,
        }
      );
      const move = response.data.move;
      setBestMove(move);
      // Optionally update the game with the returned move:
      if (move && game.move(move, { sloppy: true })) {
        setFen(game.fen());
      }
    } catch (error) {
      console.error(error);
      setBestMove("Error calculating move");
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        p: 2,
      }}
    >
      <Typography variant="h4" gutterBottom>
        Chess AI Board
      </Typography>
      <Chessboard position={fen} boardWidth={400} onPieceDrop={onDrop} />
      <Box
        sx={{
          mt: 2,
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          gap: 2,
          justifyContent: "center",
          width: "100%",
        }}
      >
        <TextField
          label="FEN"
          variant="outlined"
          value={fen}
          onChange={(e) => setFen(e.target.value)}
          helperText="Modify the FEN to set a custom board position."
        />
        <TextField
          label="Depth"
          type="number"
          variant="outlined"
          value={depth}
          onChange={(e) => setDepth(parseInt(e.target.value))}
          sx={{ width: "100px" }}
        />
        <TextField
          select
          label="Engine"
          variant="outlined"
          value={engine}
          onChange={(e) => setEngine(e.target.value)}
          sx={{ width: "150px" }}
        >
          <MenuItem value="minimax">Minimax</MenuItem>
          <MenuItem value="trained">Trained</MenuItem>
        </TextField>
      </Box>
      <Button variant="contained" sx={{ mt: 2 }} onClick={handleGetMove}>
        Get Best Move
      </Button>
      {bestMove && (
        <Typography variant="h6" sx={{ mt: 2 }}>
          Best Move: {bestMove}
        </Typography>
      )}
    </Box>
  );
}

export default ChessBoardComponent;
