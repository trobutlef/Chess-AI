import React, { useState, useEffect } from "react";
import axios from "axios";
import { Routes, Route } from "react-router-dom";
import { Box, CircularProgress, Alert, ThemeProvider, createTheme, CssBaseline } from "@mui/material";

import LoginPage from "./LoginPage";
import Register from "./components/Register";
import ChessGame from "./ChessGame";

// Configure Axios once:
axios.defaults.baseURL =
  process.env.REACT_APP_API_URL || "http://localhost:5000";
axios.defaults.withCredentials = true;

// Create a theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#9c27b0',
    },
  },
  components: {
    MuiButton: {
      defaultProps: {
        variant: 'contained',
      },
    },
  },
});

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchUser = async () => {
    try {
      const res = await axios.get("/api/me");
      if (res.data.user) setUser(res.data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const handleLogout = async () => {
    try {
      await axios.post("/api/logout");
      setUser(null);
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "100vh",
          backgroundColor: "#f5f5f5",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          p: { xs: 1, sm: 2 },
        }}
      >
        {user ? (
          <ChessGame user={user} onLogout={handleLogout} />
        ) : (
          <Routes>
            <Route path="/register" element={<Register />} />
            <Route path="*" element={<LoginPage onLogin={setUser} />} />
          </Routes>
        )}
      </Box>
    </ThemeProvider>
  );
}

export default App;
