import React, { useState, useEffect, useRef } from "react";
import { Box, Typography, Paper } from "@mui/material";

/**
 * Chess clock component that displays and manages time for both players.
 * 
 * @param {Object} props
 * @param {number} props.whiteTime - White's remaining time in milliseconds
 * @param {number} props.blackTime - Black's remaining time in milliseconds
 * @param {boolean} props.isWhiteTurn - Whether it's white's turn
 * @param {boolean} props.isRunning - Whether the clock is running
 * @param {function} props.onTimeUpdate - Callback when time changes (whiteTime, blackTime)
 * @param {function} props.onTimeout - Callback when a player runs out of time
 * @param {boolean} props.isPaused - Whether the game is paused
 */
export default function ChessClock({
  whiteTime: initialWhiteTime,
  blackTime: initialBlackTime,
  isWhiteTurn,
  isRunning,
  onTimeUpdate,
  onTimeout,
  isPaused = false,
}) {
  const [whiteTime, setWhiteTime] = useState(initialWhiteTime);
  const [blackTime, setBlackTime] = useState(initialBlackTime);
  const lastTickRef = useRef(Date.now());

  // Update internal state when props change (e.g., after a move)
  useEffect(() => {
    setWhiteTime(initialWhiteTime);
    setBlackTime(initialBlackTime);
  }, [initialWhiteTime, initialBlackTime]);

  // Tick the clock
  useEffect(() => {
    if (!isRunning || isPaused) return;

    const interval = setInterval(() => {
      const now = Date.now();
      const delta = now - lastTickRef.current;
      lastTickRef.current = now;

      if (isWhiteTurn) {
        setWhiteTime((prev) => {
          const newTime = Math.max(0, prev - delta);
          if (newTime === 0 && onTimeout) {
            onTimeout("white");
          }
          return newTime;
        });
      } else {
        setBlackTime((prev) => {
          const newTime = Math.max(0, prev - delta);
          if (newTime === 0 && onTimeout) {
            onTimeout("black");
          }
          return newTime;
        });
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isRunning, isWhiteTurn, isPaused, onTimeout]);

  // Report time updates
  useEffect(() => {
    if (onTimeUpdate) {
      onTimeUpdate(whiteTime, blackTime);
    }
  }, [whiteTime, blackTime, onTimeUpdate]);

  // Reset lastTick on turn change
  useEffect(() => {
    lastTickRef.current = Date.now();
  }, [isWhiteTurn]);

  const formatTime = (ms) => {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const tenths = Math.floor((ms % 1000) / 100);

    if (totalSeconds < 10) {
      return `${seconds}.${tenths}`;
    } else if (totalSeconds < 60) {
      return `0:${seconds.toString().padStart(2, "0")}`;
    }
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  const getClockStyle = (isActive, time) => {
    const isLow = time < 30000; // Less than 30 seconds
    const isCritical = time < 10000; // Less than 10 seconds

    return {
      backgroundColor: isActive
        ? isCritical
          ? "#ff5252"
          : isLow
          ? "#ff9800"
          : "#4caf50"
        : "#e0e0e0",
      color: isActive ? "#fff" : "#666",
      transition: "background-color 0.3s ease",
    };
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        gap: 1,
        minWidth: 120,
      }}
    >
      {/* Black's clock (top) */}
      <Paper
        elevation={!isWhiteTurn && isRunning ? 4 : 1}
        sx={{
          p: 2,
          textAlign: "center",
          borderRadius: 2,
          ...getClockStyle(!isWhiteTurn && isRunning, blackTime),
        }}
      >
        <Typography variant="caption" sx={{ opacity: 0.8 }}>
          Black
        </Typography>
        <Typography
          variant="h4"
          sx={{
            fontFamily: "monospace",
            fontWeight: "bold",
          }}
        >
          {formatTime(blackTime)}
        </Typography>
      </Paper>

      {/* White's clock (bottom) */}
      <Paper
        elevation={isWhiteTurn && isRunning ? 4 : 1}
        sx={{
          p: 2,
          textAlign: "center",
          borderRadius: 2,
          ...getClockStyle(isWhiteTurn && isRunning, whiteTime),
        }}
      >
        <Typography variant="caption" sx={{ opacity: 0.8 }}>
          White
        </Typography>
        <Typography
          variant="h4"
          sx={{
            fontFamily: "monospace",
            fontWeight: "bold",
          }}
        >
          {formatTime(whiteTime)}
        </Typography>
      </Paper>
    </Box>
  );
}

/**
 * Time control presets
 */
export const TIME_CONTROLS = {
  bullet1: { name: "Bullet 1+0", time: 60, increment: 0 },
  bullet2: { name: "Bullet 2+1", time: 120, increment: 1 },
  blitz3: { name: "Blitz 3+0", time: 180, increment: 0 },
  blitz5: { name: "Blitz 5+0", time: 300, increment: 0 },
  blitz5_3: { name: "Blitz 5+3", time: 300, increment: 3 },
  rapid10: { name: "Rapid 10+0", time: 600, increment: 0 },
  rapid15: { name: "Rapid 15+10", time: 900, increment: 10 },
  classical30: { name: "Classical 30+0", time: 1800, increment: 0 },
  unlimited: { name: "Unlimited", time: null, increment: 0 },
};
