import React, { useState, useEffect } from "react";
import axios from "axios";
import { Routes, Route } from "react-router-dom";
import { Box, CircularProgress, Alert } from "@mui/material";

import LoginPage from "./LoginPage";
import Register from "./components/Register";
import ChessGame from "./ChessGame";

// Configure Axios once:
axios.defaults.baseURL =
  process.env.REACT_APP_API_URL || "http://localhost:5001";
axios.defaults.withCredentials = true;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    axios
      .get("/api/me")
      .then((res) => {
        if (res.data.user) setUser(res.data.user);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundColor: "white",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        p: 2,
      }}
    >
      {user ? (
        <ChessGame user={user} />
      ) : (
        <Routes>
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<LoginPage onLogin={setUser} />} />
        </Routes>
      )}
    </Box>
  );
}

export default App;
