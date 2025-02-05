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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMsg("Please fill in both fields.");
      return;
    }
    setErrorMsg("");
    onLogin({ email, name: email.split("@")[0] });
  };

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
        <Box sx={{ mb: 2 }}>
          <img
            src="/logo_1.png"
            alt="Logo"
            style={{ width: "100px", marginBottom: "20px" }}
          />
        </Box>

        <Typography variant="h4" sx={{ mb: 2 }}>
          Welcome back
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

        <Divider sx={{ my: 3 }}>OR</Divider>

        <Button
          onClick={handleGoogleAuth}
          fullWidth
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "#FFFFFF",
            color: "#5F6368",
            border: "1px solid #DADCE0",
            borderRadius: "4px",
            padding: "10px 0",
            textTransform: "none",
            fontWeight: 500,
            fontSize: "14px",
            "&:hover": {
              backgroundColor: "#F7F8F8",
              borderColor: "#DADCE0",
            },
          }}
        >
          <img
            src="https://developers.google.com/identity/images/g-logo.png"
            alt="Google Logo"
            style={{ width: "20px", marginRight: "10px" }}
          />
          Sign in with Google
        </Button>
      </Box>
    </Box>
  );
}

export default LoginPage;
