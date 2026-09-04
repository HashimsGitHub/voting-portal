import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navigation = ({ user, onLogout }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <Link to="/elections" className="navbar-brand">
        <img src="https://stnustksaalumni.blob.core.windows.net/site-images/NUST-logo.png" alt="NUST logo" />
        NUST Alumni Elections
      </Link>
      <div className="navbar-links">
        <Link to="/elections">Elections</Link>
        {user?.role === 'admin' && <Link to="/admin">Admin</Link>}
        {user?.role === 'candidate' && <Link to="/candidate/profile">My Profile</Link>}
        {user ? (
          <>
            <span className="navbar-user">{user.email}</span>
            <button onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
