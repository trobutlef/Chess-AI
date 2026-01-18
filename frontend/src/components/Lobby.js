import React, { useState, useEffect, useCallback } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import AddIcon from "@mui/icons-material/Add";
import { TIME_CONTROLS } from "./ChessClock";

/**
 * Multiplayer lobby component for creating and joining games.
 * 
 * @param {Object} props.socket - Socket.io client instance
 * @param {function} props.onGameStart - Callback when a game starts
 * @param {Object} props.user - Current user
 */
export default function Lobby({ socket, onGameStart, user }) {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [timeControl, setTimeControl] = useState("blitz5");
  const [creatingRoom, setCreatingRoom] = useState(false);
  const [waitingRoom, setWaitingRoom] = useState(null);

  // Fetch rooms
  const fetchRooms = useCallback(() => {
    if (socket && socket.connected) {
      socket.emit("get_rooms");
    }
  }, [socket]);

  useEffect(() => {
    if (!socket) return;

    // Socket event handlers
    const handleConnect = () => {
      setLoading(false);
      fetchRooms();
    };

    const handleRoomList = (roomList) => {
      setRooms(roomList);
      setLoading(false);
    };

    const handleRoomListUpdated = (roomList) => {
      setRooms(roomList);
    };

    const handleRoomCreated = (room) => {
      setCreatingRoom(false);
      setCreateDialogOpen(false);
      setWaitingRoom(room);
    };

    const handleGameStarted = (room) => {
      setWaitingRoom(null);
      onGameStart(room);
    };

    const handleError = (err) => {
      setError(err.message);
      setCreatingRoom(false);
    };

    const handleOpponentLeft = () => {
      setError("Opponent left the game");
      setWaitingRoom(null);
    };

    // Register listeners
    socket.on("connect", handleConnect);
    socket.on("room_list", handleRoomList);
    socket.on("room_list_updated", handleRoomListUpdated);
    socket.on("room_created", handleRoomCreated);
    socket.on("game_started", handleGameStarted);
    socket.on("error", handleError);
    socket.on("opponent_left", handleOpponentLeft);

    // Initial fetch
    if (socket.connected) {
      handleConnect();
    }

    // Cleanup
    return () => {
      socket.off("connect", handleConnect);
      socket.off("room_list", handleRoomList);
      socket.off("room_list_updated", handleRoomListUpdated);
      socket.off("room_created", handleRoomCreated);
      socket.off("game_started", handleGameStarted);
      socket.off("error", handleError);
      socket.off("opponent_left", handleOpponentLeft);
    };
  }, [socket, fetchRooms, onGameStart]);

  const handleCreateRoom = () => {
    setCreatingRoom(true);
    socket.emit("create_room", {
      time_control: TIME_CONTROLS[timeControl].time,
    });
  };

  const handleJoinRoom = (roomId) => {
    socket.emit("join_room", { room_id: roomId });
  };

  const handleCancelWaiting = () => {
    if (waitingRoom) {
      socket.emit("leave_room", { room_id: waitingRoom.id });
      setWaitingRoom(null);
    }
  };

  const formatTimeControl = (seconds) => {
    if (!seconds) return "Unlimited";
    const minutes = Math.floor(seconds / 60);
    return `${minutes} min`;
  };

  // Waiting for opponent screen
  if (waitingRoom) {
    return (
      <Paper sx={{ p: 4, textAlign: "center", maxWidth: 400, mx: "auto" }}>
        <Typography variant="h5" sx={{ mb: 3 }}>
          Waiting for Opponent
        </Typography>
        <CircularProgress sx={{ mb: 3 }} />
        <Typography color="textSecondary" sx={{ mb: 2 }}>
          Time Control: {formatTimeControl(waitingRoom.time_control)}
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          Share this room with a friend or wait for someone to join.
        </Typography>
        <Button variant="outlined" color="error" onClick={handleCancelWaiting}>
          Cancel
        </Button>
      </Paper>
    );
  }

  return (
    <Box sx={{ maxWidth: 600, mx: "auto" }}>
      <Typography variant="h5" sx={{ mb: 2, textAlign: "center" }}>
        Multiplayer Lobby
      </Typography>

      {error && (
        <Alert severity="error" onClose={() => setError("")} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: "flex", gap: 1, mb: 2, justifyContent: "center" }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Game
        </Button>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchRooms}
        >
          Refresh
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
          <CircularProgress />
        </Box>
      ) : rooms.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: "center" }}>
          <Typography color="textSecondary">
            No games available. Create one to get started!
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Host</TableCell>
                <TableCell>Time Control</TableCell>
                <TableCell align="right">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rooms.map((room) => (
                <TableRow key={room.id} hover>
                  <TableCell>{room.host_name}</TableCell>
                  <TableCell>
                    <Chip
                      label={formatTimeControl(room.time_control)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      variant="contained"
                      onClick={() => handleJoinRoom(room.id)}
                    >
                      Join
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create Room Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)}>
        <DialogTitle>Create New Game</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Time Control</InputLabel>
            <Select
              value={timeControl}
              onChange={(e) => setTimeControl(e.target.value)}
              label="Time Control"
            >
              {Object.entries(TIME_CONTROLS).map(([key, tc]) => (
                <MenuItem key={key} value={key}>
                  {tc.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateRoom}
            variant="contained"
            disabled={creatingRoom}
          >
            {creatingRoom ? <CircularProgress size={24} /> : "Create"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
