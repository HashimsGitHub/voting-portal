import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import '../styles/Elections.css';

const Elections = () => {
  const [elections, setElections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchElections();
  }, []);

  const fetchElections = async () => {
    try {
      setLoading(true);
      const response = await apiService.getElections(null);
      const list = response.elections || [];
      setElections(list);
      setError(null);

      const featured = list.find(el => el.status === 'active') || list[0];
      if (featured) {
        fetchStats(featured._id);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching elections:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async (electionId) => {
    try {
      const response = await apiService.getElectionStats(electionId);
      if (response.success) {
        setStats(response.stats);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
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
      <div className="site-hero">
        <div>
          <p className="eyebrow">NAA KSA</p>
          <h1>2026 NAA KSA Executive Council Election</h1>
          <p>Participate in shaping the future of the alumni association</p>
        </div>
      </div>

      {stats && (
        <div className="stats-dashboard">
          <div className="stat-card">
            <div className="stat-icon seats">🪑</div>
            <div className="stat-value">{stats.total_seats}</div>
            <div className="stat-label">Total Seats</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon candidates">🧑‍💼</div>
            <div className="stat-value">{stats.total_candidates}</div>
            <div className="stat-label">Total Candidates</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon voters">🗳️</div>
            <div className="stat-value">{stats.total_registered_voters}</div>
            <div className="stat-label">Registered Voters</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon turnout">📊</div>
            <div className="stat-value">{(stats.turnout_percentage || 0).toFixed(1)}%</div>
            <div className="stat-label">Voter Turnout</div>
          </div>

          <div className="stats-bar-chart">
            {[
              { label: 'Seats', value: stats.total_seats, className: 'bar-seats' },
              { label: 'Candidates', value: stats.total_candidates, className: 'bar-candidates' },
              { label: 'Registered Voters', value: stats.total_registered_voters, className: 'bar-voters' },
              { label: 'Votes Cast', value: stats.total_votes_cast, className: 'bar-cast' }
            ].map(bar => {
              const max = Math.max(stats.total_seats, stats.total_candidates, stats.total_registered_voters, stats.total_votes_cast, 1);
              const widthPct = Math.max((bar.value / max) * 100, 2);
              return (
                <div className="bar-row" key={bar.label}>
                  <span className="bar-row-label">{bar.label}</span>
                  <div className="bar-track">
                    <div className={`bar-fill ${bar.className}`} style={{ width: `${widthPct}%` }}></div>
                  </div>
                  <span className="bar-row-value">{bar.value}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {elections.length === 0 ? (
        <div className="no-elections">
          <p>No election found</p>
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
