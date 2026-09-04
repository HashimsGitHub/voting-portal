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
  const [filterPosition, setFilterPosition] = useState(null);
  const [voteChoice, setVoteChoice] = useState({});
  const [votedPositions, setVotedPositions] = useState({});
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

      // Default each candidate's vote choice to the first seat they're running for
      const defaults = {};
      allCandidates.forEach(c => {
        if (c.positions && c.positions.length > 0) {
          defaults[c._id] = c.positions[0];
        }
      });
      setVoteChoice(defaults);

      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (candidateId, candidateName) => {
    const position = voteChoice[candidateId];
    if (!position) {
      alert('This candidate has not been assigned a seat yet');
      return;
    }
    if (!window.confirm(`Vote for ${candidateName} for ${position}?`)) {
      return;
    }

    try {
      const response = await apiService.castVote(electionId, candidateId, position);
      if (response.success) {
        setVotedPositions(prev => ({
          ...prev,
          [position]: candidateId
        }));
        alert(`Vote recorded for ${candidateName}!`);
        setTimeout(() => navigate(`/elections/${electionId}/results`), 1500);
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to cast vote: ${err.message}`);
    }
  };

  const filteredCandidates = filterPosition
    ? candidates.filter(c => (c.positions || []).includes(filterPosition))
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

      {positions.length > 0 && (
        <div className="position-filter">
          <h3>Filter by Seat:</h3>
          <div className="position-buttons">
            <button
              className={`position-btn ${filterPosition === null ? 'active' : ''}`}
              onClick={() => setFilterPosition(null)}
            >
              All Seats
            </button>
            {positions.map(position => (
              <button
                key={position}
                className={`position-btn ${filterPosition === position ? 'active' : ''}`}
                onClick={() => setFilterPosition(position)}
              >
                {position}
              </button>
            ))}
          </div>
        </div>
      )}

      {filteredCandidates.length === 0 ? (
        <div className="no-candidates">
          <p>No candidates found for this seat</p>
        </div>
      ) : (
        <div className="candidates-grid">
          {filteredCandidates.map(candidate => {
            const candidatePositions = candidate.positions || [];
            const hasSeat = candidatePositions.length > 0;
            const chosenPosition = voteChoice[candidate._id];
            const alreadyVotedForChoice = chosenPosition && votedPositions[chosenPosition] === candidate._id;

            return (
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
                  <p className="candidate-position">
                    {hasSeat ? candidatePositions.join(', ') : 'No seat assigned yet'}
                  </p>

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

                  {voting && hasSeat && (
                    <div className="vote-controls">
                      {candidatePositions.length > 1 && (
                        <select
                          className="vote-position-select"
                          value={chosenPosition}
                          onChange={(e) => setVoteChoice(prev => ({ ...prev, [candidate._id]: e.target.value }))}
                        >
                          {candidatePositions.map(p => (
                            <option key={p} value={p}>{p}</option>
                          ))}
                        </select>
                      )}
                      <button
                        className={`btn-vote-large ${alreadyVotedForChoice ? 'voted' : ''}`}
                        onClick={() => handleVote(candidate._id, candidate.name)}
                        disabled={alreadyVotedForChoice}
                      >
                        {alreadyVotedForChoice ? 'Vote Recorded' : `Vote for ${chosenPosition}`}
                      </button>
                    </div>
                  )}

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
            );
          })}
        </div>
      )}
    </div>
  );
};

export default CandidateProfiles;
