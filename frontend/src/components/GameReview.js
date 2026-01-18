import React, { useState, useMemo } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Button,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Slider,
} from "@mui/material";
import FirstPageIcon from "@mui/icons-material/FirstPage";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import LastPageIcon from "@mui/icons-material/LastPage";
import CloseIcon from "@mui/icons-material/Close";

/**
 * Game review component for stepping through past games.
 * 
 * @param {Object} props.game - Game object with pgn and metadata
 * @param {function} props.onClose - Callback to close the review
 */
export default function GameReview({ game, onClose }) {
  const [moveIndex, setMoveIndex] = useState(0);

  // Parse PGN and create positions
  const { positions, movesSan } = useMemo(() => {
    const chess = new Chess();
    const positionsArr = [chess.fen()];
    const movesSanArr = [];

    if (game.pgn) {
      // Parse the simple PGN format: "1. e4 e5 2. Nf3 Nc6"
      const tokens = game.pgn.split(/\s+/).filter((t) => t && !t.match(/^\d+\.$/));
      const moveTokens = tokens.filter((t) => !t.includes("."));

      for (const san of moveTokens) {
        try {
          const move = chess.move(san);
          if (move) {
            positionsArr.push(chess.fen());
            movesSanArr.push(san);
          }
        } catch {
          // Invalid move, stop parsing
          break;
        }
      }
    }

    return { positions: positionsArr, movesSan: movesSanArr };
  }, [game.pgn]);

  const currentFen = positions[moveIndex];

  const handleFirst = () => setMoveIndex(0);
  const handlePrev = () => setMoveIndex((i) => Math.max(0, i - 1));
  const handleNext = () => setMoveIndex((i) => Math.min(positions.length - 1, i + 1));
  const handleLast = () => setMoveIndex(positions.length - 1);

  const handleKeyDown = (e) => {
    if (e.key === "ArrowLeft") handlePrev();
    else if (e.key === "ArrowRight") handleNext();
    else if (e.key === "Home") handleFirst();
    else if (e.key === "End") handleLast();
  };

  // Format moves for display
  const formattedMoves = useMemo(() => {
    const rows = [];
    for (let i = 0; i < movesSan.length; i += 2) {
      rows.push({
        number: Math.floor(i / 2) + 1,
        white: movesSan[i] || "",
        black: movesSan[i + 1] || "",
        whiteIndex: i + 1,
        blackIndex: i + 2,
      });
    }
    return rows;
  }, [movesSan]);

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        gap: 2,
        p: 2,
      }}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="h5">Game Review</Typography>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>

      <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
        {/* Chess board */}
        <Box>
          <Chessboard
            position={currentFen}
            boardWidth={400}
            arePiecesDraggable={false}
            boardOrientation={game.user_color || "white"}
          />
          
          {/* Navigation controls */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              gap: 1,
              mt: 2,
            }}
          >
            <IconButton onClick={handleFirst} disabled={moveIndex === 0}>
              <FirstPageIcon />
            </IconButton>
            <IconButton onClick={handlePrev} disabled={moveIndex === 0}>
              <NavigateBeforeIcon />
            </IconButton>
            <Typography sx={{ alignSelf: "center", minWidth: 80, textAlign: "center" }}>
              {moveIndex} / {positions.length - 1}
            </Typography>
            <IconButton onClick={handleNext} disabled={moveIndex === positions.length - 1}>
              <NavigateNextIcon />
            </IconButton>
            <IconButton onClick={handleLast} disabled={moveIndex === positions.length - 1}>
              <LastPageIcon />
            </IconButton>
          </Box>

          {/* Position slider */}
          <Box sx={{ px: 2, mt: 1 }}>
            <Slider
              value={moveIndex}
              onChange={(_, val) => setMoveIndex(val)}
              min={0}
              max={positions.length - 1}
              step={1}
            />
          </Box>
        </Box>

        {/* Move list */}
        <Paper sx={{ width: 200, maxHeight: 400, overflow: "auto" }}>
          <Table size="small">
            <TableBody>
              {formattedMoves.map((row) => (
                <TableRow key={row.number}>
                  <TableCell sx={{ width: 30, color: "text.secondary" }}>
                    {row.number}.
                  </TableCell>
                  <TableCell
                    onClick={() => setMoveIndex(row.whiteIndex)}
                    sx={{
                      cursor: "pointer",
                      backgroundColor:
                        moveIndex === row.whiteIndex ? "action.selected" : "inherit",
                      "&:hover": { backgroundColor: "action.hover" },
                    }}
                  >
                    {row.white}
                  </TableCell>
                  <TableCell
                    onClick={() => row.black && setMoveIndex(row.blackIndex)}
                    sx={{
                      cursor: row.black ? "pointer" : "default",
                      backgroundColor:
                        moveIndex === row.blackIndex ? "action.selected" : "inherit",
                      "&:hover": row.black
                        ? { backgroundColor: "action.hover" }
                        : {},
                    }}
                  >
                    {row.black}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </Box>

      {/* Game info */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="body2" color="textSecondary">
          <strong>Result:</strong> {game.result || "In progress"} |{" "}
          <strong>Engine:</strong> {game.engine || "N/A"} |{" "}
          <strong>Color:</strong> {game.user_color || "white"}
        </Typography>
      </Paper>

      <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
        <Button variant="outlined" onClick={onClose}>
          Close
        </Button>
      </Box>
    </Box>
  );
}
