import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import '../styles/CandidateProfiles.css';

const CandidateProfiles = ({ voting = false }) => {
  const { electionId } = useParams();
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [votedCandidates, setVotedCandidates] = useState({});
  const [positions, setPositions] = useState([]);

  useEffect(() => {
    fetchCandidates();
  }, [electionId]);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      const response = await apiService.getCandidates(electionId);
      const allCandidates = response.candidates || [];
      setCandidates(allCandidates);

      // Extract unique positions across all candidates (a candidate can run for up to 3)
      const uniquePositions = [...new Set(allCandidates.flatMap(c => c.positions || []))];
      setPositions(uniquePositions);
      if (uniquePositions.length > 0) {
        setSelectedPosition(uniquePositions[0]);
      }

      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (candidateId, candidateName) => {
    if (!selectedPosition) {
      alert('Please select a position first');
      return;
    }
    if (!window.confirm(`Vote for ${candidateName} for ${selectedPosition}?`)) {
      return;
    }

    try {
      const response = await apiService.castVote(electionId, candidateId, selectedPosition);
      if (response.success) {
        setVotedCandidates(prev => ({
          ...prev,
          [selectedPosition]: candidateId
        }));
        alert(`Vote recorded for ${candidateName}!`);
        // Optionally navigate to results after voting
        setTimeout(() => navigate(`/elections/${electionId}/results`), 1500);
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to cast vote: ${err.message}`);
    }
  };

  const filteredCandidates = selectedPosition
    ? candidates.filter(c => (c.positions || []).includes(selectedPosition))
    : candidates;

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div className="candidates-container">
      <div className="candidates-header">
        <h1>{voting ? 'Cast Your Vote' : 'Candidate Profiles'}</h1>
        <p>Learn about the candidates and {voting ? 'vote for your choice' : 'their platforms'}</p>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      {positions.length > 1 && (
        <div className="position-filter">
          <h3>Select Position:</h3>
          <div className="position-buttons">
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
        <div className="no-candidates">
          <p>No candidates found for this position</p>
        </div>
      ) : (
        <div className="candidates-grid">
          {filteredCandidates.map(candidate => (
            <div key={candidate._id} className="candidate-card">
              {candidate.image_url && (
                <img 
                  src={candidate.image_url} 
                  alt={candidate.name}
                  className="candidate-image"
                />
              )}
              
              <div className="candidate-content">
                <h2>{candidate.name}</h2>
                <p className="candidate-position">{(candidate.positions || []).join(', ')}</p>

                {candidate.batch_year && (
                  <p className="candidate-detail">
                    <strong>Batch:</strong> {candidate.batch_year}
                  </p>
                )}

                {candidate.department && (
                  <p className="candidate-detail">
                    <strong>Department:</strong> {candidate.department}
                  </p>
                )}

                <div className="candidate-bio">
                  <h4>About</h4>
                  <p>{candidate.bio}</p>
                </div>

                {candidate.platform && (
                  <div className="candidate-platform">
                    <h4>Platform</h4>
                    <p>{candidate.platform}</p>
                  </div>
                )}

                <div className="candidate-stats">
                  <div className="stat">
                    <span className="stat-value">{candidate.vote_count}</span>
                    <span className="stat-label">Votes</span>
                  </div>
                </div>

                {voting ? (
                  <button
                    className={`btn-vote-large ${votedCandidates[selectedPosition] === candidate._id ? 'voted' : ''}`}
                    onClick={() => handleVote(candidate._id, candidate.name)}
                    disabled={votedCandidates[selectedPosition] === candidate._id}
                  >
                    {votedCandidates[selectedPosition] === candidate._id ? 'Vote Recorded' : 'Vote for This Candidate'}
                  </button>
                ) : null}

                {candidate.contact_email && (
                  <p className="candidate-email">
                    <a href={`mailto:${candidate.contact_email}`}>
                      Contact: {candidate.contact_email}
                    </a>
                  </p>
                )}

                {candidate.linkedin_url && (
                  <p className="candidate-email">
                    <a href={candidate.linkedin_url} target="_blank" rel="noopener noreferrer">
                      LinkedIn Profile
                    </a>
                  </p>
                )}

                {candidate.social_url && (
                  <p className="candidate-email">
                    <a href={candidate.social_url} target="_blank" rel="noopener noreferrer">
                      Social Media
                    </a>
                  </p>
                )}

                {candidate.campaign_media && candidate.campaign_media.length > 0 && (
                  <div className="candidate-campaign-media">
                    <h4>Campaign Media</h4>
                    <div className="candidate-campaign-media-grid">
                      {candidate.campaign_media.map((item) => (
                        item.media_type === 'video' ? (
                          <video key={item.url} src={item.url} controls />
                        ) : (
                          <img key={item.url} src={item.url} alt="Campaign media" />
                        )
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CandidateProfiles;
