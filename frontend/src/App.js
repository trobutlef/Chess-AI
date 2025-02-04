// frontend/src/App.js
import React, { useState } from "react";
import LoginPage from "./LoginPage";
import ChessBoardComponent from "./ChessBoard";
import { CssBaseline, Box } from "@mui/material";

function App() {
  const [user, setUser] = useState(null);

  return (
    <>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "100vh",
          backgroundColor: "#f0f2f5",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          p: 2,
        }}
      >
        {user ? <ChessBoardComponent /> : <LoginPage onLogin={setUser} />}
      </Box>
    </>
  );
}

export default App;
