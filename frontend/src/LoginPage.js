import React, { useState } from "react";
import axios from "axios";
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMsg("Please fill in both fields.");
      return;
    }
    setErrorMsg("");
    try {
      const endpoint = isRegister ? "/api/register" : "/api/login";
      const response = await axios.post(
        endpoint,
        { email, password, name: email.split("@")[0] },
        { withCredentials: true }
      );
      if (response.data.message) {
        onLogin({ email, name: email.split("@")[0] });
      } else {
        setErrorMsg(response.data.error || "Authentication failed");
      }
    } catch (error) {
      const errMsg =
        error.response?.data?.error ||
        error.message ||
        "An unknown error occurred";
      setErrorMsg(errMsg);
    }
  };

  const handleGoogleAuth = () => {
    const base = process.env.REACT_APP_API_URL || "";
    window.location.href = `${base}/login/google`;
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
        <Typography variant="h4" sx={{ mb: 2 }}>
          {isRegister ? "Register" : "Welcome Back"}
        </Typography>

        {errorMsg && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {errorMsg}
          </Alert>
        )}

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

        <Typography variant="body2" sx={{ mt: 2 }}>
          {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
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

        <Divider sx={{ my: 3 }}>OR</Divider>

        <Button
          onClick={handleGoogleAuth}
          fullWidth
          startIcon={<GoogleIcon />}
          sx={{
            backgroundColor: "#FFF",
            color: "#5F6368",
            border: "1px solid #DADCE0",
            borderRadius: 1,
            padding: "10px 0",
            textTransform: "none",
            fontWeight: 500,
            fontSize: "14px",
            "&:hover": { backgroundColor: "#F7F8F8" },
          }}
        >
          Sign in with Google
        </Button>
      </Box>
    </Box>
  );
}

export default LoginPage;
