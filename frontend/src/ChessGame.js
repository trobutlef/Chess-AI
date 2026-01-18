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
  Select,
  MenuItem,
  InputLabel,
  Tabs,
  Tab,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import ChessClock, { TIME_CONTROLS } from "./components/ChessClock";
import GameHistory from "./components/GameHistory";
import GameReview from "./components/GameReview";

// Configure your API base URL in .env as REACT_APP_API_URL
axios.defaults.baseURL =
  process.env.REACT_APP_API_URL || "http://localhost:5000";
axios.defaults.withCredentials = true;

export default function ChessGame({ user, onLogout }) {
  // Game state
  const [fen, setFen] = useState(new Chess().fen());
  const [moveList, setMoveList] = useState([]);
  const [engine, setEngine] = useState("minimax");
  const [depth, setDepth] = useState(3);
  const [userSide, setUserSide] = useState(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMessage, setDialogMessage] = useState("");
  const [premoveFrom, setPremoveFrom] = useState(null);
  const [premoveQueue, setPremoveQueue] = useState([]);
  const [loadingAI, setLoadingAI] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  // Time control state
  const [timeControl, setTimeControl] = useState("blitz5"); // Key in TIME_CONTROLS
  const [whiteTime, setWhiteTime] = useState(300000); // 5 min in ms
  const [blackTime, setBlackTime] = useState(300000);
  const [clockRunning, setClockRunning] = useState(false);

  // Game persistence state
  const [currentGameId, setCurrentGameId] = useState(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState(0); // 0 = Play, 1 = History
  const [reviewGame, setReviewGame] = useState(null);

  const gameRef = useRef(new Chess());
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  // Update move history
  const updateMoveList = useCallback((moveObj) => {
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
  }, []);

  // Save move to server
  const saveMoveToServer = useCallback(async (san, result = null) => {
    if (!currentGameId) return;
    
    try {
      await axios.post(`/api/games/${currentGameId}/move`, {
        move: san,
        white_time: whiteTime,
        black_time: blackTime,
        result: result,
      });
    } catch (err) {
      console.error("Failed to save move:", err);
    }
  }, [currentGameId, whiteTime, blackTime]);

  // Game over detection
  const checkGameOver = useCallback(() => {
    const g = gameRef.current;
    if (!g.isGameOver()) return null;
    
    let msg = "Game Over: ";
    let result = "1/2-1/2";
    
    if (g.isCheckmate()) {
      if (g.turn() === "w") {
        msg += "Black wins by checkmate";
        result = "0-1";
      } else {
        msg += "White wins by checkmate";
        result = "1-0";
      }
    } else if (g.isStalemate()) {
      msg += "Draw by stalemate";
    } else if (g.isInsufficientMaterial()) {
      msg += "Draw by insufficient material";
    } else if (g.isThreefoldRepetition()) {
      msg += "Draw by repetition";
    } else {
      msg += "Draw";
    }
    
    setClockRunning(false);
    setDialogMessage(msg);
    setDialogOpen(true);
    
    return result;
  }, []);

  // Handle timeout
  const handleTimeout = useCallback((color) => {
    const winner = color === "white" ? "Black" : "White";
    const result = color === "white" ? "0-1" : "1-0";
    
    setClockRunning(false);
    setDialogMessage(`Time's up! ${winner} wins on time.`);
    setDialogOpen(true);
    
    if (currentGameId) {
      saveMoveToServer(null, result);
    }
  }, [currentGameId, saveMoveToServer]);

  // Ask AI for move
  const makeAIMove = useCallback(async () => {
    if (gameRef.current.isGameOver()) return;

    setLoadingAI(true);
    setErrorMsg("");

    try {
      const resp = await axios.post("/api/chess/move", {
        fen: gameRef.current.fen(),
        engine,
        depth,
        use_book: true,
      });

      const m = resp.data.move;
      if (m) {
        const aiMove = gameRef.current.move(m, { sloppy: true });
        if (aiMove) {
          updateMoveList(aiMove);
          saveMoveToServer(aiMove.san);
          setFen(gameRef.current.fen());
          const result = checkGameOver();
          if (result) {
            saveMoveToServer(null, result);
          }
        }
      }
    } catch (err) {
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
          saveMoveToServer(userMove.san);
          setFen(gameRef.current.fen());
          const result = checkGameOver();
          if (result) {
            saveMoveToServer(null, result);
          } else {
            makeAIMove();
          }
        }
      } catch {
        // ignore illegal premove
      }
    }
  }, [engine, depth, premoveQueue, updateMoveList, checkGameOver, saveMoveToServer]);

  // Create game on server
  const createGameOnServer = useCallback(async (side, selectedEngine, selectedDepth, selectedTimeControl) => {
    try {
      const tc = TIME_CONTROLS[selectedTimeControl];
      const res = await axios.post("/api/games", {
        engine: selectedEngine,
        depth: selectedDepth,
        user_color: side,
        time_control: tc.time,
        opponent_type: "ai",
      });
      setCurrentGameId(res.data.id);
      return res.data;
    } catch (err) {
      console.error("Failed to create game:", err);
      return null;
    }
  }, []);

  // Reset/start game
  const resetGame = useCallback(async () => {
    const newGame = new Chess();
    gameRef.current = newGame;
    setFen(newGame.fen());
    setMoveList([]);
    setDialogOpen(false);
    setPremoveFrom(null);
    setPremoveQueue([]);
    setErrorMsg("");
    
    // Set time based on time control
    const tc = TIME_CONTROLS[timeControl];
    if (tc.time) {
      const timeMs = tc.time * 1000;
      setWhiteTime(timeMs);
      setBlackTime(timeMs);
      setClockRunning(true);
    } else {
      setWhiteTime(null);
      setBlackTime(null);
      setClockRunning(false);
    }
  }, [timeControl]);

  const handleSideSelection = async (side) => {
    const chosen =
      side === "random" ? (Math.random() < 0.5 ? "white" : "black") : side;
    setUserSide(chosen);
    
    // Create game on server
    await createGameOnServer(chosen, engine, depth, timeControl);
    
    setGameStarted(true);
    await resetGame();
    
    if (chosen === "black") {
      makeAIMove();
    }
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
      saveMoveToServer(move.san);
      setFen(g.fen());
      const result = checkGameOver();
      if (result) {
        saveMoveToServer(null, result);
      } else {
        makeAIMove();
      }
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

  // Handle time updates
  const handleTimeUpdate = useCallback((wt, bt) => {
    setWhiteTime(wt);
    setBlackTime(bt);
  }, []);

  // Handle reviewing a game
  const handleReviewGame = (game) => {
    setReviewGame(game);
  };

  // If reviewing a game, show review component
  if (reviewGame) {
    return (
      <GameReview
        game={reviewGame}
        onClose={() => setReviewGame(null)}
      />
    );
  }

  // Side selection screen
  if (!gameStarted) {
    return (
      <Box sx={{ p: 4, textAlign: "center", maxWidth: 600, mx: "auto" }}>
        <Typography variant="h4" sx={{ mb: 3 }}>
          Chess AI
        </Typography>
        <Typography sx={{ mb: 2 }}>Welcome, {user.name}!</Typography>

        <Tabs
          value={activeTab}
          onChange={(_, v) => setActiveTab(v)}
          centered
          sx={{ mb: 3 }}
        >
          <Tab label="Play" />
          <Tab label="Game History" />
        </Tabs>

        {activeTab === 0 ? (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Game Settings
            </Typography>

            {/* Engine selection */}
            <FormControl component="fieldset" sx={{ mb: 2 }}>
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
                  label="Neural Network"
                />
              </RadioGroup>
            </FormControl>

            {/* Depth selector (only for minimax) */}
            {engine === "minimax" && (
              <Box sx={{ mb: 2 }}>
                <TextField
                  label="Search Depth"
                  type="number"
                  value={depth}
                  onChange={(e) => setDepth(parseInt(e.target.value, 10) || 1)}
                  inputProps={{ min: 1, max: 6 }}
                  sx={{ width: 120 }}
                  size="small"
                />
              </Box>
            )}

            {/* Time control selector */}
            <FormControl sx={{ mb: 3, minWidth: 200 }}>
              <InputLabel>Time Control</InputLabel>
              <Select
                value={timeControl}
                onChange={(e) => setTimeControl(e.target.value)}
                label="Time Control"
                size="small"
              >
                {Object.entries(TIME_CONTROLS).map(([key, tc]) => (
                  <MenuItem key={key} value={key}>
                    {tc.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Typography variant="h6" sx={{ mb: 2 }}>
              Choose Your Side
            </Typography>
            <Stack direction="row" spacing={2} justifyContent="center">
              <Button
                variant="contained"
                onClick={() => handleSideSelection("white")}
                sx={{ bgcolor: "#fff", color: "#000", "&:hover": { bgcolor: "#eee" } }}
              >
                White
              </Button>
              <Button
                variant="contained"
                onClick={() => handleSideSelection("black")}
                sx={{ bgcolor: "#333", "&:hover": { bgcolor: "#444" } }}
              >
                Black
              </Button>
              <Button
                variant="outlined"
                onClick={() => handleSideSelection("random")}
              >
                Random
              </Button>
            </Stack>
          </Paper>
        ) : (
          <GameHistory onReviewGame={handleReviewGame} />
        )}

        <Button
          onClick={onLogout}
          sx={{ mt: 3 }}
          color="inherit"
        >
          Logout
        </Button>
      </Box>
    );
  }

  // Game screen
  const boardWidth = isMobile ? Math.min(window.innerWidth - 32, 360) : 400;
  const isWhiteTurn = gameRef.current.turn() === "w";

  return (
    <>
      {errorMsg && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {errorMsg}
        </Alert>
      )}

      <Box
        sx={{
          display: "flex",
          flexDirection: isMobile ? "column" : "row",
          gap: 2,
          p: 2,
          alignItems: isMobile ? "center" : "flex-start",
        }}
      >
        {/* Chess clock - left side on desktop, top on mobile */}
        {TIME_CONTROLS[timeControl].time && (
          <Box sx={{ order: isMobile ? 0 : -1 }}>
            <ChessClock
              whiteTime={whiteTime}
              blackTime={blackTime}
              isWhiteTurn={isWhiteTurn}
              isRunning={clockRunning && !dialogOpen}
              onTimeUpdate={handleTimeUpdate}
              onTimeout={handleTimeout}
            />
          </Box>
        )}

        {/* Board and controls */}
        <Box>
          <Typography variant="h6" align="center" sx={{ mb: 1 }}>
            {engine === "neural" ? "Neural Network AI" : "Minimax AI"} (Depth: {depth})
          </Typography>
          <Chessboard
            position={fen}
            boardWidth={boardWidth}
            onPieceDrop={onPieceDrop}
            onSquareClick={onSquareClick}
            onSquareRightClick={onSquareRightClick}
            customSquareStyles={customStyles}
            boardOrientation={userSide}
          />
          <Box
            sx={{
              mt: 2,
              display: "flex",
              flexWrap: "wrap",
              gap: 1,
              justifyContent: "center",
            }}
          >
            <Button
              variant="outlined"
              onClick={() => {
                setGameStarted(false);
                setCurrentGameId(null);
              }}
            >
              New Game
            </Button>
          </Box>
        </Box>

        {/* Move list */}
        <Paper
          sx={{
            width: isMobile ? "100%" : 200,
            maxHeight: 400,
            overflow: "auto",
          }}
        >
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

      {/* Game over dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Game Over</DialogTitle>
        <DialogContent>
          <Typography>{dialogMessage}</Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setDialogOpen(false);
              setGameStarted(false);
              setCurrentGameId(null);
            }}
          >
            New Game
          </Button>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Loading indicator */}
      {loadingAI && (
        <Box sx={{ position: "fixed", top: 16, right: 16 }}>
          <CircularProgress />
        </Box>
      )}
    </>
  );
}
