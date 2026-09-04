import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiService } from '../services/api';
import '../styles/LiveResults.css';

const LiveResults = () => {
  const { electionId } = useParams();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedPosition, setSelectedPosition] = useState(null);

  useEffect(() => {
    fetchResults();
    
    if (autoRefresh) {
      const interval = setInterval(fetchResults, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [electionId, autoRefresh]);

  const fetchResults = async () => {
    try {
      const response = await apiService.getLiveResults(electionId);
      if (response.success) {
        setResults(response);
        setError(null);
        
        // Extract unique positions if not already selected
        const candidates = response.candidates || [];
        const positions = [...new Set(candidates.map(c => c.position))];
        if (!selectedPosition && positions.length > 0) {
          setSelectedPosition(positions[0]);
        }
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching results:', err);
    } finally {
      setLoading(false);
    }
  };

  const getProgressPercentage = (candidate) => {
    if (!results || results.total_votes === 0) return 0;
    return (candidate.vote_count / results.total_votes) * 100;
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  const allCandidates = results?.candidates || [];
  const positions = [...new Set(allCandidates.map(c => c.position))];
  
  const filteredCandidates = selectedPosition
    ? allCandidates.filter(c => c.position === selectedPosition)
    : allCandidates;

  return (
    <div className="results-container">
      <div className="results-header">
        <h1>Live Election Results</h1>
        <p>Real-time voting statistics</p>
      </div>

      <div className="results-controls">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          />
          Auto-refresh (every 5 seconds)
        </label>
        <button 
          className="btn btn-refresh"
          onClick={fetchResults}
        >
          Refresh Now
        </button>
      </div>

      <div className="results-stats">
        <div className="stat-card">
          <h3>Total Votes</h3>
          <p className="stat-number">{results?.total_votes || 0}</p>
        </div>
        {results?.voter_stats && (
          <>
            <div className="stat-card">
              <h3>Registered Voters</h3>
              <p className="stat-number">{results.voter_stats.total_registered || 0}</p>
            </div>
            <div className="stat-card">
              <h3>Turnout</h3>
              <p className="stat-percentage">
                {(results.voter_stats.turnout_percentage || 0).toFixed(1)}%
              </p>
            </div>
          </>
        )}
      </div>

      {positions.length > 1 && (
        <div className="position-filter">
          <h3>View Results by Position:</h3>
          <div className="position-buttons">
            <button
              className={`position-btn ${!selectedPosition ? 'active' : ''}`}
              onClick={() => setSelectedPosition(null)}
            >
              All Positions
            </button>
            {positions.map(position => (
              <button
                key={position}
                className={`position-btn ${selectedPosition === position ? 'active' : ''}`}
                onClick={() => setSelectedPosition(position)}
              >
                {position}
              </button>
            ))}
          </div>
        </div>
      )}

      {filteredCandidates.length === 0 ? (
        <div className="no-results">
          <p>No voting data available yet</p>
        </div>
      ) : (
        <div className="results-section">
          <div className="results-list">
            {filteredCandidates
              .sort((a, b) => b.vote_count - a.vote_count)
              .map((candidate, index) => (
                <div key={candidate.candidate_id} className="result-item">
                  <div className="result-rank">#{index + 1}</div>
                  
                  <div className="result-content">
                    <h3>{candidate.name}</h3>
                    <p className="result-position">{candidate.position}</p>
                    {candidate.bio && (
                      <p className="result-bio">{candidate.bio}</p>
                    )}
                  </div>

                  <div className="result-stats-detail">
                    <div className="votes-info">
                      <span className="vote-count">{candidate.vote_count}</span>
                      <span className="vote-label">votes</span>
                    </div>
                    <div className="percentage">
                      {candidate.vote_percentage.toFixed(1)}%
                    </div>
                  </div>

                  <div className="progress-container">
                    <div 
                      className="progress-bar"
                      style={{
                        width: `${getProgressPercentage(candidate)}%`
                      }}
                    ></div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      <div className="results-footer">
        <p className="last-updated">
          Last updated: {new Date().toLocaleTimeString()}
          {autoRefresh && ' (auto-refreshing)'}
        </p>
      </div>
    </div>
  );
};

export default LiveResults;
