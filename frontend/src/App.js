import React, { useState } from "react";
import LoginPage from "./LoginPage";
import ChessGame from "./ChessGame";
import { Box } from "@mui/material";

function App() {
  const [user, setUser] = useState(null);

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
      {user ? <ChessGame user={user} /> : <LoginPage onLogin={setUser} />}
    </Box>
  );
}

export default App;
