// src/components/PrivateRoute.js
import React from "react";
import { Navigate } from "react-router-dom";
import { getAuth } from "firebase/auth";

const PrivateRoute = ({ component: Component }) => {
  const auth = getAuth();
  const user = auth.currentUser;

  return user ? <Component /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;
