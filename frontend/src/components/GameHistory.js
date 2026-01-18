import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import DeleteIcon from "@mui/icons-material/Delete";
import DownloadIcon from "@mui/icons-material/Download";

/**
 * Game history component that displays past games and allows review.
 * 
 * @param {function} props.onReviewGame - Callback when user wants to review a game
 */
export default function GameHistory({ onReviewGame }) {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [gameToDelete, setGameToDelete] = useState(null);

  const fetchGames = async () => {
    try {
      const res = await axios.get("/api/games");
      setGames(res.data.games || []);
    } catch (err) {
      console.error("Failed to fetch games:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGames();
  }, []);

  const handleDelete = async () => {
    if (!gameToDelete) return;
    
    try {
      await axios.delete(`/api/games/${gameToDelete.id}`);
      setGames(games.filter((g) => g.id !== gameToDelete.id));
    } catch (err) {
      console.error("Failed to delete game:", err);
    } finally {
      setDeleteDialogOpen(false);
      setGameToDelete(null);
    }
  };

  const downloadPGN = (game) => {
    const blob = new Blob([game.pgn || ""], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `game_${game.id}.pgn`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getResultChip = (result, userColor) => {
    if (result === "*") {
      return <Chip label="In Progress" size="small" />;
    }
    
    const isWin =
      (result === "1-0" && userColor === "white") ||
      (result === "0-1" && userColor === "black");
    const isLoss =
      (result === "0-1" && userColor === "white") ||
      (result === "1-0" && userColor === "black");
    
    if (isWin) {
      return <Chip label="Win" size="small" color="success" />;
    } else if (isLoss) {
      return <Chip label="Loss" size="small" color="error" />;
    } else {
      return <Chip label="Draw" size="small" color="warning" />;
    }
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  };

  const formatTimeControl = (seconds) => {
    if (!seconds) return "Unlimited";
    const minutes = Math.floor(seconds / 60);
    return `${minutes} min`;
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (games.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: "center" }}>
        <Typography color="textSecondary">
          No games played yet. Start a new game to see your history!
        </Typography>
      </Paper>
    );
  }

  return (
    <>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Opponent</TableCell>
              <TableCell>Color</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Result</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {games.map((game) => (
              <TableRow key={game.id} hover>
                <TableCell>{formatDate(game.created_at)}</TableCell>
                <TableCell>
                  {game.opponent_type === "ai"
                    ? `AI (${game.engine})`
                    : "Human"}
                </TableCell>
                <TableCell>
                  <Chip
                    label={game.user_color}
                    size="small"
                    variant="outlined"
                    sx={{
                      borderColor:
                        game.user_color === "white" ? "#333" : "#000",
                      backgroundColor:
                        game.user_color === "white" ? "#fff" : "#333",
                      color: game.user_color === "white" ? "#000" : "#fff",
                    }}
                  />
                </TableCell>
                <TableCell>{formatTimeControl(game.time_control)}</TableCell>
                <TableCell>
                  {getResultChip(game.result, game.user_color)}
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => onReviewGame && onReviewGame(game)}
                    title="Review game"
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => downloadPGN(game)}
                    title="Download PGN"
                  >
                    <DownloadIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => {
                      setGameToDelete(game);
                      setDeleteDialogOpen(true);
                    }}
                    title="Delete game"
                    color="error"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Game</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this game? This action cannot be
            undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
