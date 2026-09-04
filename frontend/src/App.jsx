import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Navigation from './components/Navigation';
import Login from './pages/Login';
import Elections from './pages/Elections';
import ElectionDetail from './pages/ElectionDetail';
import CandidateProfiles from './pages/CandidateProfiles';
import LiveResults from './pages/LiveResults';
import AdminDashboard from './pages/AdminDashboard';
import CandidateProfile from './pages/CandidateProfile';
import PrivateRoute from './components/PrivateRoute';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = JSON.parse(atob(token.split('.')[1]));
        setUser(decoded);
      } catch (e) {
        console.error('Invalid token:', e);
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (loading) {
    return <div className="loading-container"><div className="spinner"></div></div>;
  }

  return (
    <Router>
      <div className="app">
        <Navigation user={user} onLogout={handleLogout} />
        <main className="main-content">
          <Routes>
            <Route path="/login" element={<Login onLogin={handleLogin} />} />
            <Route path="/elections" element={<Elections />} />
            <Route 
              path="/elections/:electionId" 
              element={<ElectionDetail user={user} />} 
            />
            <Route 
              path="/elections/:electionId/candidates" 
              element={<CandidateProfiles />} 
            />
            <Route 
              path="/elections/:electionId/vote" 
              element={
                <PrivateRoute user={user}>
                  <CandidateProfiles voting={true} />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/elections/:electionId/results" 
              element={<LiveResults />} 
            />
            <Route
              path="/admin"
              element={
                <PrivateRoute user={user} requiredRole="admin">
                  <AdminDashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/candidate/profile"
              element={
                <PrivateRoute user={user} requiredRole="candidate">
                  <CandidateProfile />
                </PrivateRoute>
              }
            />
            <Route path="/" element={<Navigate to="/elections" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
