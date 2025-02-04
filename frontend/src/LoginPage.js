import React, { useState } from "react";
import axios from "axios";
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Link,
  Alert,
} from "@mui/material";
import GoogleIcon from "@mui/icons-material/Google";

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [message, setMessage] = useState("");

  const handleEmailAuth = async (e) => {
    e.preventDefault();
    try {
      if (isRegister) {
        const res = await axios.post("http://127.0.0.1:5000/api/register", {
          email,
          password,
          name: email,
        });
        setMessage(res.data.message);
      } else {
        const res = await axios.post("http:///127.0.0.1:5000/api/login", {
          email,
          password,
        });
        setMessage(res.data.message);
        onLogin({ email });
      }
    } catch (err) {
      console.error(err);
      setMessage(err.response?.data?.error || "An error occurred");
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = "http:///127.0.0.1:5000/login/google";
  };

  return (
    <Container maxWidth="xs">
      <Box sx={{ textAlign: "center", mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Chess AI
        </Typography>
      </Box>
      <Box
        component="form"
        onSubmit={handleEmailAuth}
        sx={{
          p: 3,
          border: "1px solid #e0e0e0",
          borderRadius: 2,
          boxShadow: 2,
          backgroundColor: "#fff",
        }}
      >
        <Typography variant="h5" component="h2" align="center" gutterBottom>
          {isRegister ? "Register" : "Login"}
        </Typography>
        {message && (
          <Alert severity="info" sx={{ mb: 2 }}>
            {message}
          </Alert>
        )}
        <TextField
          label="Email"
          type="email"
          variant="outlined"
          fullWidth
          margin="normal"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <TextField
          label="Password"
          type="password"
          variant="outlined"
          fullWidth
          margin="normal"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
          {isRegister ? "Register" : "Login"}
        </Button>
        <Box sx={{ mt: 2, textAlign: "center" }}>
          <Link
            component="button"
            variant="body2"
            onClick={() => setIsRegister(!isRegister)}
          >
            {isRegister
              ? "Already have an account? Login"
              : "Don't have an account? Register"}
          </Link>
        </Box>
      </Box>
      <Box sx={{ mt: 3 }}>
        <Button
          variant="outlined"
          fullWidth
          startIcon={<GoogleIcon />}
          onClick={handleGoogleLogin}
          sx={{
            textTransform: "none",
            borderColor: "#e0e0e0",
            color: "#555",
            "&:hover": {
              borderColor: "#bdbdbd",
            },
          }}
        >
          Continue with Google
        </Button>
      </Box>
    </Container>
  );
}

export default LoginPage;
