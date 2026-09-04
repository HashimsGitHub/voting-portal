import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import '../styles/Login.css';

const Login = ({ onLogin }) => {
  const navigate = useNavigate();
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'voter' });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const response = mode === 'login'
        ? await apiService.login(form.email, form.password)
        : await apiService.register(form);

      if (response.token) {
        onLogin(response.token, response.user);
        navigate('/elections');
      } else {
        setError(response.error || 'Authentication failed');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>{mode === 'login' ? 'Login' : 'Create Account'}</h1>
        <p>
          {mode === 'login'
            ? 'Sign in to vote in active elections'
            : 'Register to participate in alumni elections'}
        </p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          {mode === 'register' && (
            <>
              <div className="form-group">
                <label>Full Name</label>
                <input type="text" name="name" value={form.name} onChange={handleChange} required />
              </div>

              <div className="form-group">
                <label>I am registering as a</label>
                <select name="role" value={form.role} onChange={handleChange}>
                  <option value="voter">Voter</option>
                  <option value="candidate">Candidate</option>
                </select>
                {form.role === 'candidate' && (
                  <p className="field-hint">
                    Use the same email the admin added you with — your candidate profile
                    will link automatically so you can edit your photo, bio and profile link.
                  </p>
                )}
              </div>
            </>
          )}

          <div className="form-group">
            <label>Email</label>
            <input type="email" name="email" value={form.email} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              required
              minLength={6}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Please wait...' : mode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>

        <p className="login-toggle">
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            type="button"
            className="link-btn"
            onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
          >
            {mode === 'login' ? 'Register' : 'Login'}
          </button>
        </p>

        <Link to="/elections" className="back-link">Back to Elections</Link>
      </div>
    </div>
  );
};

export default Login;
