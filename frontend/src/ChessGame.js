import React, { useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import axios from "axios";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  Paper,
  Stack,
} from "@mui/material";

function ChessGame({ user }) {
  // Initialize chess.js game instance
  const [game, setGame] = useState(new Chess());
  const [fen, setFen] = useState(game.fen());
  const [moveList, setMoveList] = useState([]);
  const [engine, setEngine] = useState("minimax");
  const [userSide, setUserSide] = useState(null);
  const [gameStarted, setGameStarted] = useState(false);

  // Reset the game state
  const resetGame = () => {
    const newGame = new Chess();
    setGame(newGame);
    setFen(newGame.fen());
    setMoveList([]);
  };

  // Handle side selection (white, black, or random)
  const handleSideSelection = (side) => {
    let chosenSide = side;
    if (side === "random") {
      chosenSide = Math.random() < 0.5 ? "white" : "black";
    }
    setUserSide(chosenSide);
    setGameStarted(true);
    resetGame();
  };

  // Update move list after a move
  const updateMoveList = (moveObj) => {
    const san = moveObj.san;
    const isWhiteMove = game.history().length % 2 === 1;
    setMoveList((prev) => {
      if (isWhiteMove) {
        return [
          ...prev,
          {
            moveNumber: Math.ceil((prev.length + 1) / 2),
            white: san,
            black: "",
          },
        ];
      } else {
        const updated = [...prev];
        updated[updated.length - 1].black = san;
        return updated;
      }
    });
  };

  // Called when user drops a piece
  const onDrop = (sourceSquare, targetSquare) => {
    if (game.turn() !== userSide[0]) return false; // Check if it's user's turn
    const move = game.move({
      from: sourceSquare,
      to: targetSquare,
      promotion: "q",
    });
    if (move === null) return false; // Illegal move
    updateMoveList(move);
    setFen(game.fen());
    setGame(new Chess(game.fen()));
    // Let AI move after a short delay if game not over
    setTimeout(() => {
      if (!game.game_over() && game.turn() !== userSide[0]) {
        makeAIMove();
      }
    }, 300);
    return true;
  };

  // Call backend to get AI move
  const makeAIMove = async () => {
    try {
      const response = await axios.post(
        "http://localhost:5000/api/chess/move",
        {
          fen: game.fen(),
          engine: engine,
          depth: 3,
        }
      );
      if (response.data.move) {
        const aiMove = game.move(response.data.move, { sloppy: true });
        if (aiMove) {
          updateMoveList(aiMove);
          setFen(game.fen());
          setGame(new Chess(game.fen()));
        }
      }
    } catch (error) {
      console.error("Error fetching AI move:", error);
    }
  };

  // If game hasn't started, display side selection and reset button
  if (!gameStarted) {
    return (
      <Box sx={{ p: 4, textAlign: "center" }}>
        <Typography variant="h4" gutterBottom>
          Choose Your Side
        </Typography>
        <Stack
          direction="row"
          spacing={2}
          justifyContent="center"
          sx={{ mb: 2 }}
        >
          <Button
            variant="contained"
            onClick={() => handleSideSelection("white")}
          >
            Play as White
          </Button>
          <Button
            variant="contained"
            onClick={() => handleSideSelection("black")}
          >
            Play as Black
          </Button>
          <Button
            variant="contained"
            onClick={() => handleSideSelection("random")}
          >
            Random Side
          </Button>
        </Stack>
        <Typography variant="subtitle1">Welcome, {user.name}!</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "row", gap: 4, p: 2 }}>
      {/* Left side: Chessboard and controls */}
      <Box>
        {/* AI Engine Header */}
        <Box sx={{ mb: 2, textAlign: "center" }}>
          <Typography variant="h5">
            {engine === "neural" ? "Neural Network" : "Minimax"} (AI)
          </Typography>
        </Box>
        <Chessboard
          position={fen}
          boardWidth={400}
          onPieceDrop={onDrop}
          boardOrientation={userSide} // User's chosen side determines board orientation.
        />
        <Box sx={{ mt: 2, textAlign: "center" }}>
          <Button variant="outlined" onClick={resetGame} sx={{ mr: 2 }}>
            Reset Game
          </Button>
          <FormControl component="fieldset" sx={{ display: "inline-block" }}>
            <FormLabel component="legend">Engine</FormLabel>
            <RadioGroup
              row
              value={engine}
              onChange={(e) => setEngine(e.target.value)}
            >
              <FormControlLabel
                value="minimax"
                control={<Radio />}
                label="Minimax"
              />
              <FormControlLabel
                value="neural"
                control={<Radio />}
                label="Neural Network"
              />
            </RadioGroup>
          </FormControl>
        </Box>
        <Box sx={{ mt: 2, textAlign: "center" }}>
          <Typography variant="subtitle1">{user.name} (You)</Typography>
        </Box>
      </Box>

      {/* Right side: Move list */}
      <Box>
        <Paper sx={{ width: 300, maxHeight: 400, overflow: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>#</TableCell>
                <TableCell>White</TableCell>
                <TableCell>Black</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {moveList.map((row, index) => (
                <TableRow key={index}>
                  <TableCell>{row.moveNumber}</TableCell>
                  <TableCell>{row.white}</TableCell>
                  <TableCell>{row.black}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </Box>
    </Box>
  );
}

export default ChessGame;
