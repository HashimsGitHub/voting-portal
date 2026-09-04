import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import '../styles/Elections.css';

const Elections = () => {
  const [elections, setElections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('active');

  useEffect(() => {
    fetchElections();
  }, [filter]);

  const fetchElections = async () => {
    try {
      setLoading(true);
      const response = await apiService.getElections(filter !== 'all' ? filter : null);
      setElections(response.elections || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching elections:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'status-active';
      case 'draft': return 'status-draft';
      case 'closed': return 'status-closed';
      case 'completed': return 'status-completed';
      default: return 'status-default';
    }
  };

  const getStatusBadge = (status) => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div className="elections-container">
      <div className="elections-header">
        <h1>NUST Alumni Elections</h1>
        <p>Participate in shaping the future of the alumni association</p>
      </div>

      <div className="filter-section">
        <button 
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All Elections
        </button>
        <button 
          className={`filter-btn ${filter === 'active' ? 'active' : ''}`}
          onClick={() => setFilter('active')}
        >
          Active
        </button>
        <button 
          className={`filter-btn ${filter === 'draft' ? 'active' : ''}`}
          onClick={() => setFilter('draft')}
        >
          Upcoming
        </button>
        <button 
          className={`filter-btn ${filter === 'closed' ? 'active' : ''}`}
          onClick={() => setFilter('closed')}
        >
          Closed
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {elections.length === 0 ? (
        <div className="no-elections">
          <p>No elections found in this category</p>
        </div>
      ) : (
        <div className="elections-grid">
          {elections.map(election => (
            <div key={election._id} className="election-card">
              <div className="election-card-header">
                <h2>{election.title}</h2>
                <span className={`status-badge ${getStatusColor(election.status)}`}>
                  {getStatusBadge(election.status)}
                </span>
              </div>

              <p className="election-description">{election.description}</p>

              <div className="election-info">
                <div className="info-item">
                  <span className="info-label">Total Seats:</span>
                  <span className="info-value">{election.total_seats}</span>
                </div>
                {election.start_date && (
                  <div className="info-item">
                    <span className="info-label">Starts:</span>
                    <span className="info-value">
                      {new Date(election.start_date).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="election-actions">
                <Link 
                  to={`/elections/${election._id}`}
                  className="btn btn-primary"
                >
                  View Details
                </Link>
                <Link 
                  to={`/elections/${election._id}/candidates`}
                  className="btn btn-secondary"
                >
                  Candidates
                </Link>
                {election.status === 'active' && (
                  <Link 
                    to={`/elections/${election._id}/vote`}
                    className="btn btn-vote"
                  >
                    Vote Now
                  </Link>
                )}
                <Link 
                  to={`/elections/${election._id}/results`}
                  className="btn btn-results"
                >
                  Live Results
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Elections;
