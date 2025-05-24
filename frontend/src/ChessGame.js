import React, { useState, useRef, useCallback } from "react";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  Paper,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  TextField,
} from "@mui/material";

// Configure your API base URL in .env as REACT_APP_API_URL
axios.defaults.baseURL =
  process.env.REACT_APP_API_URL || "http://localhost:5001";
axios.defaults.withCredentials = true;

export default function ChessGame({ user }) {
  const [fen, setFen] = useState(new Chess().fen());
  const [moveList, setMoveList] = useState([]);
  const [engine, setEngine] = useState("minimax");
  const [depth, setDepth] = useState(2); // default lowered depth
  const [userSide, setUserSide] = useState(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMessage, setDialogMessage] = useState("");
  const [premoveFrom, setPremoveFrom] = useState(null);
  const [premoveQueue, setPremoveQueue] = useState([]);
  const [loadingAI, setLoadingAI] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const gameRef = useRef(new Chess());

  // Update move history
  const updateMoveList = (moveObj) => {
    const san = moveObj.san;
    setMoveList((prev) => {
      const updated = [...prev];
      if (gameRef.current.history().length % 2 === 1) {
        updated.push({ moveNumber: updated.length + 1, white: san, black: "" });
      } else {
        updated[updated.length - 1].black = san;
      }
      return updated;
    });
  };

  // Game over detection
  const checkGameOver = () => {
    const g = gameRef.current;
    if (!g.isGameOver()) return;
    let msg = "Game Over: ";
    if (g.isCheckmate()) {
      msg +=
        g.turn() === "w"
          ? "Black wins by checkmate"
          : "White wins by checkmate";
    } else if (g.isStalemate()) {
      msg += "Draw by stalemate";
    } else if (g.isInsufficientMaterial()) {
      msg += "Draw by insufficient material";
    } else if (g.isThreefoldRepetition()) {
      msg += "Draw by repetition";
    } else {
      msg += "Draw";
    }
    setDialogMessage(msg);
    setDialogOpen(true);
  };

  // Ask AI for move, with console timing
  const makeAIMove = useCallback(async () => {
    if (gameRef.current.isGameOver()) return;

    setLoadingAI(true);
    setErrorMsg("");
    console.time("minimax");

    try {
      const resp = await axios.post("/api/chess/move", {
        fen: gameRef.current.fen(),
        engine,
        depth, // use the state depth
      });
      console.timeEnd("minimax");

      const m = resp.data.move;
      if (m) {
        const aiMove = gameRef.current.move(m, { sloppy: true });
        if (aiMove) {
          updateMoveList(aiMove);
          setFen(gameRef.current.fen());
          checkGameOver();
        }
      }
    } catch (err) {
      console.timeEnd("minimax");
      console.error("AI move error:", err);
      setErrorMsg("Failed to get AI move");
    } finally {
      setLoadingAI(false);
    }

    // Execute any queued premove
    if (premoveQueue.length && !gameRef.current.isGameOver()) {
      const [{ from, to }, ...rest] = premoveQueue;
      setPremoveQueue(rest);
      try {
        const userMove = gameRef.current.move({
          from,
          to,
          promotion: "q",
          sloppy: true,
        });
        if (userMove) {
          updateMoveList(userMove);
          setFen(gameRef.current.fen());
          checkGameOver();
          await makeAIMove();
        }
      } catch {
        // ignore illegal premove
      }
    }
  }, [engine, depth, premoveQueue]);

  // Reset/start game
  const resetGame = () => {
    const newGame = new Chess();
    gameRef.current = newGame;
    setFen(newGame.fen());
    setMoveList([]);
    setDialogOpen(false);
    setPremoveFrom(null);
    setPremoveQueue([]);
    if (userSide === "black") makeAIMove();
  };

  const handleSideSelection = (side) => {
    const chosen =
      side === "random" ? (Math.random() < 0.5 ? "white" : "black") : side;
    setUserSide(chosen);
    setGameStarted(true);
    resetGame();
  };

  // Handle drop on your turn
  const onPieceDrop = (from, to) => {
    const g = gameRef.current;
    const userTurn = userSide === "white" ? "w" : "b";
    if (g.turn() !== userTurn) return false;
    if (from === to) return false;

    try {
      const move = g.move({ from, to, promotion: "q", sloppy: true });
      if (!move) return false;
      updateMoveList(move);
      setFen(g.fen());
      checkGameOver();
      makeAIMove();
      return true;
    } catch {
      return false;
    }
  };

  // Two-click premove UI
  const onSquareClick = (sq) => {
    const g = gameRef.current;
    if (g.turn() === (userSide === "white" ? "w" : "b")) {
      setPremoveFrom(null);
      return;
    }
    if (!premoveFrom) {
      const piece = g.get(sq);
      if (!piece || (piece.color === "w" ? "white" : "black") !== userSide) {
        return;
      }
      setPremoveFrom(sq);
      return;
    }
    if (premoveFrom === sq) {
      setPremoveFrom(null);
      return;
    }
    const legal = g
      .moves({ verbose: true })
      .some((m) => m.from === premoveFrom && m.to === sq);
    if (legal) {
      setPremoveQueue((prev) => [...prev, { from: premoveFrom, to: sq }]);
    }
    setPremoveFrom(null);
  };

  const onSquareRightClick = () => {
    setPremoveFrom(null);
    setPremoveQueue([]);
  };

  const customStyles = {};
  if (premoveFrom) {
    customStyles[premoveFrom] = { backgroundColor: "rgba(255,0,0,0.4)" };
  }

  if (!gameStarted) {
    return (
      <Box sx={{ p: 4, textAlign: "center" }}>
        <Typography variant="h4">Choose Your Side</Typography>
        <Stack
          direction="row"
          spacing={2}
          justifyContent="center"
          sx={{ mt: 2 }}
        >
          <Button onClick={() => handleSideSelection("white")}>White</Button>
          <Button onClick={() => handleSideSelection("black")}>Black</Button>
          <Button onClick={() => handleSideSelection("random")}>Random</Button>
        </Stack>
        <Typography sx={{ mt: 2 }}>Welcome, {user.name}!</Typography>
      </Box>
    );
  }

  return (
    <>
      {errorMsg && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {errorMsg}
        </Alert>
      )}

      <Box sx={{ display: "flex", gap: 4, p: 2 }}>
        <Box>
          <Typography variant="h5" align="center">
            {engine === "neural" ? "Neural Network AI" : "Minimax AI"}
          </Typography>
          <Chessboard
            position={fen}
            boardWidth={400}
            onPieceDrop={onPieceDrop}
            onSquareClick={onSquareClick}
            onSquareRightClick={onSquareRightClick}
            customSquareStyles={customStyles}
            boardOrientation={userSide}
          />
          <Box sx={{ mt: 2, display: "flex", alignItems: "center", gap: 2 }}>
            <TextField
              label="Depth"
              type="number"
              variant="outlined"
              value={depth}
              onChange={(e) => setDepth(parseInt(e.target.value, 10) || 1)}
              sx={{ width: 100 }}
              inputProps={{ min: 1, max: 6 }}
            />
            <Button onClick={resetGame}>Reset</Button>
            <FormControl component="fieldset">
              <FormLabel>Engine</FormLabel>
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
                  label="Neural"
                />
              </RadioGroup>
            </FormControl>
          </Box>
        </Box>

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
              {moveList.map((row, i) => (
                <TableRow key={i}>
                  <TableCell>{row.moveNumber}</TableCell>
                  <TableCell>{row.white}</TableCell>
                  <TableCell>{row.black}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </Box>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Game Over</DialogTitle>
        <DialogContent>
          <Typography>{dialogMessage}</Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setDialogOpen(false);
              resetGame();
            }}
          >
            New Game
          </Button>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {loadingAI && (
        <Box sx={{ position: "fixed", top: 16, right: 16 }}>
          <CircularProgress />
        </Box>
      )}
    </>
  );
}
