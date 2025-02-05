import React, { useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Divider,
  Link,
  Alert,
} from "@mui/material";
import GoogleIcon from "@mui/icons-material/Google";

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [isRegister, setIsRegister] = useState(false);

  // Handle form submission (for email/password login or sign-up)
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMsg("Please fill in both fields.");
      return;
    }
    setErrorMsg("");
    // Here, you'd normally call your backend API for login or registration.
    // For demonstration purposes, we simulate a successful login.
    onLogin({ email, name: email.split("@")[0] });
  };

  // Redirect to the backend's Google OAuth endpoint.
  const handleGoogleAuth = () => {
    window.location.href = "http://localhost:5000/login/google";
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundColor: "white",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Box
        sx={{
          width: 400,
          backgroundColor: "white",
          p: 4,
          boxShadow: 0,
          borderRadius: 2,
          textAlign: "center",
        }}
      >
        {/* Logo */}
        <Box sx={{ mb: 2 }}>
          <img
            src="/logo_1.png"
            alt="Logo"
            style={{ width: "100px", marginBottom: "20px" }}
          />
        </Box>

        {/* Title */}
        <Typography variant="h4" sx={{ mb: 2 }}>
          Welcome back
        </Typography>

        {/* Error Message */}
        {errorMsg && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {errorMsg}
          </Alert>
        )}

        {/* Login/Sign-Up Form */}
        <form onSubmit={handleSubmit}>
          <TextField
            label="Email"
            variant="outlined"
            fullWidth
            margin="normal"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            label="Password"
            variant="outlined"
            type="password"
            fullWidth
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
            {isRegister ? "Sign Up" : "Login"}
          </Button>
        </form>

        {/* Toggle between Login and Sign Up */}
        <Typography variant="body2" sx={{ mt: 2 }}>
          {isRegister ? "Already have an account? " : "Don't have an account? "}
          <Link
            href="#"
            onClick={(e) => {
              e.preventDefault();
              setIsRegister(!isRegister);
            }}
          >
            {isRegister ? "Login" : "Sign Up"}
          </Link>
        </Typography>

        {/* Divider with "OR" */}
        <Divider sx={{ my: 3 }}>OR</Divider>

        {/* Google Auth Button */}
        <Button
          variant="outlined"
          startIcon={<GoogleIcon />}
          onClick={handleGoogleAuth}
          fullWidth
        >
          Continue with Google
        </Button>
      </Box>
    </Box>
  );
}

export default LoginPage;
