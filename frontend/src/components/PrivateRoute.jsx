import React from 'react';
import { Navigate } from 'react-router-dom';

const PrivateRoute = ({ user, requiredRole, children }) => {
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/elections" replace />;
  }

  return children;
};

export default PrivateRoute;
