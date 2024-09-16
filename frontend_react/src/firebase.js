// src/firebase.js
import { initializeApp } from "firebase/app";

const firebaseConfig = {
  apiKey: "YOUR_FIREBASE_API_KEY",
  authDomain: "your-app.firebaseapp.com",
  projectId: "your-app-id",
  // ... other configuration options
};

const app = initializeApp(firebaseConfig);

export default app;
