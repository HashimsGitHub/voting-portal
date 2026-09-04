import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import '../styles/ElectionDetail.css';

const ElectionDetail = () => {
  const { electionId } = useParams();
  const [election, setElection] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [voterStats, setVoterStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDetails();
  }, [electionId]);

  const fetchDetails = async () => {
    try {
      setLoading(true);
      const response = await apiService.getElectionDetails(electionId);
      if (response.success) {
        setElection(response.election);
        setCandidates(response.candidates || []);
        setVoterStats(response.voter_stats);
        setError(null);
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  if (error || !election) {
    return <div className="error-message">{error || 'Election not found'}</div>;
  }

  const positions = [...new Set(candidates.flatMap(c => c.positions || []))];

  return (
    <div className="election-detail-container">
      <div className="election-detail-header">
        <h1>{election.title}</h1>
        <span className={`status-badge status-${election.status}`}>{election.status}</span>
      </div>

      <p className="election-description">{election.description}</p>

      <div className="election-meta">
        <div><strong>Total Seats:</strong> {election.total_seats}</div>
        <div><strong>Positions:</strong> {positions.length}</div>
        {voterStats && (
          <div><strong>Turnout:</strong> {(voterStats.turnout_percentage || 0).toFixed(1)}%</div>
        )}
      </div>

      <div className="election-detail-actions">
        <Link to={`/elections/${electionId}/candidates`} className="btn btn-secondary">
          View Candidates
        </Link>
        {election.status === 'active' && (
          <Link to={`/elections/${electionId}/vote`} className="btn btn-vote">
            Vote Now
          </Link>
        )}
        <Link to={`/elections/${electionId}/results`} className="btn btn-results">
          Live Results
        </Link>
      </div>
    </div>
  );
};

export default ElectionDetail;
