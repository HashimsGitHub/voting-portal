import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/AdminDashboard.css';

const MAX_POSITIONS_PER_CANDIDATE = 3;

const emptyCandidate = {
  name: '',
  positions: [],
  bio: '',
  image_url: '',
  batch_year: '',
  department: '',
  contact_email: '',
  platform: '',
  linkedin_url: '',
  social_url: ''
};

const emptyVoter = {
  name: '',
  email: '',
  password: '',
  role: 'voter'
};

const emptyPosition = { name: '', region: '', description: '' };

const PositionCheckboxes = ({ availablePositions, selected, onChange }) => {
  const toggle = (name) => {
    if (selected.includes(name)) {
      onChange(selected.filter(p => p !== name));
    } else {
      if (selected.length >= MAX_POSITIONS_PER_CANDIDATE) {
        alert(`A candidate can run for at most ${MAX_POSITIONS_PER_CANDIDATE} positions`);
        return;
      }
      onChange([...selected, name]);
    }
  };

  if (availablePositions.length === 0) {
    return <p className="field-hint">No positions/seats have been created yet. Add some in the Positions/Seats tab first.</p>;
  }

  return (
    <div className="position-checkbox-group">
      {availablePositions.map(p => (
        <label key={p._id} className="position-checkbox">
          <input
            type="checkbox"
            checked={selected.includes(p.name)}
            onChange={() => toggle(p.name)}
          />
          {p.name}{p.region ? ` (${p.region})` : ''}
        </label>
      ))}
    </div>
  );
};

const AdminDashboard = () => {
  const [elections, setElections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('elections');

  const [positions, setPositions] = useState([]);
  const [newPosition, setNewPosition] = useState(emptyPosition);
  const [editingPositionId, setEditingPositionId] = useState(null);
  const [editPosition, setEditPosition] = useState(emptyPosition);

  const [candidates, setCandidates] = useState([]);
  const [editingCandidateId, setEditingCandidateId] = useState(null);
  const [editCandidate, setEditCandidate] = useState(emptyCandidate);
  const [selectedElection, setSelectedElection] = useState(null);

  const [users, setUsers] = useState([]);
  const [newVoter, setNewVoter] = useState(emptyVoter);
  const [editingUserId, setEditingUserId] = useState(null);
  const [editUser, setEditUser] = useState({ name: '', email: '', role: 'voter' });

  useEffect(() => {
    fetchElections();
  }, []);

  useEffect(() => {
    if (selectedElection) {
      fetchCandidates(selectedElection);
      fetchPositions(selectedElection);
    } else {
      setCandidates([]);
      setPositions([]);
    }
  }, [selectedElection]);

  useEffect(() => {
    if (activeTab === 'voters') {
      fetchUsers();
    }
  }, [activeTab]);

  const fetchElections = async () => {
    try {
      setLoading(true);
      const response = await apiService.getElections();
      const list = response.elections || [];
      setElections(list);
      if (list.length > 0) {
        setSelectedElection(list[0]._id);
      }
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching elections:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCandidates = async (electionId) => {
    try {
      const response = await apiService.getCandidates(electionId);
      setCandidates(response.candidates || []);
    } catch (err) {
      console.error('Error fetching candidates:', err);
    }
  };

  const fetchPositions = async (electionId) => {
    try {
      const response = await apiService.getPositions(electionId);
      setPositions(response.positions || []);
    } catch (err) {
      console.error('Error fetching positions:', err);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await apiService.getUsers();
      setUsers(response.users || []);
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  };

  const handleCreatePosition = async (e) => {
    e.preventDefault();
    if (!selectedElection) {
      alert('Please select an election first');
      return;
    }
    try {
      const response = await apiService.createPosition(selectedElection, newPosition);
      if (response.success) {
        setNewPosition(emptyPosition);
        fetchPositions(selectedElection);
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to create position: ${err.message}`);
    }
  };

  const startEditPosition = (position) => {
    setEditingPositionId(position._id);
    setEditPosition({
      name: position.name || '',
      region: position.region || '',
      description: position.description || ''
    });
  };

  const handleUpdatePosition = async (e) => {
    e.preventDefault();
    try {
      const response = await apiService.updatePosition(editingPositionId, editPosition);
      if (response.success) {
        setEditingPositionId(null);
        fetchPositions(selectedElection);
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to update position: ${err.message}`);
    }
  };

  const handleDeletePosition = async (positionId, name) => {
    if (!window.confirm(`Delete position "${name}"?`)) return;
    try {
      const response = await apiService.deletePosition(positionId);
      if (response.success) {
        fetchPositions(selectedElection);
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to delete position: ${err.message}`);
    }
  };

  const startEditCandidate = (candidate) => {
    setEditingCandidateId(candidate._id);
    setEditCandidate({
      name: candidate.name || '',
      positions: candidate.positions || [],
      bio: candidate.bio || '',
      image_url: candidate.image_url || '',
      batch_year: candidate.batch_year || '',
      department: candidate.department || '',
      contact_email: candidate.contact_email || '',
      platform: candidate.platform || '',
      linkedin_url: candidate.linkedin_url || '',
      social_url: candidate.social_url || ''
    });
  };

  const handleUpdateCandidate = async (e) => {
    e.preventDefault();
    if (editCandidate.positions.length === 0) {
      alert('A candidate must run for at least one position');
      return;
    }
    try {
      const updates = {
        ...editCandidate,
        batch_year: editCandidate.batch_year ? parseInt(editCandidate.batch_year) : null
      };
      const response = await apiService.updateCandidate(editingCandidateId, updates);
      if (response.success) {
        setEditingCandidateId(null);
        fetchCandidates(selectedElection);
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to update candidate: ${err.message}`);
    }
  };

  const handleDeleteCandidate = async (candidateId, name) => {
    if (!window.confirm(`Delete candidate "${name}"? This cannot be undone.`)) return;
    try {
      const response = await apiService.deleteCandidate(candidateId);
      if (response.success) {
        fetchCandidates(selectedElection);
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to delete candidate: ${err.message}`);
    }
  };

  const handleOpenNominations = async (electionId) => {
    try {
      const response = await apiService.openNominations(electionId);
      if (response.success) {
        alert('Candidates can now select their seats!');
        fetchElections();
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to open nominations: ${err.message}`);
    }
  };

  const handleActivateElection = async (electionId) => {
    if (!window.confirm('Start the election? Candidates will no longer be able to change their seats, and voters can begin voting.')) return;
    try {
      const response = await apiService.activateElection(electionId);
      if (response.success) {
        alert('Election started!');
        fetchElections();
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to start election: ${err.message}`);
    }
  };

  const handleCloseElection = async (electionId) => {
    if (window.confirm('Are you sure you want to close this election?')) {
      try {
        const response = await apiService.closeElection(electionId, true);
        if (response.success) {
          alert('Election closed!');
          fetchElections();
        } else {
          alert(`Error: ${response.error}`);
        }
      } catch (err) {
        alert(`Failed to close election: ${err.message}`);
      }
    }
  };

  const handleCreateVoter = async (e) => {
    e.preventDefault();
    try {
      const response = await apiService.createUser(newVoter);
      if (response.success) {
        alert('Account created successfully!');
        setNewVoter(emptyVoter);
        fetchUsers();
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to create account: ${err.message}`);
    }
  };

  const startEditUser = (user) => {
    setEditingUserId(user._id);
    setEditUser({ name: user.name || '', email: user.email || '', role: user.role || 'voter' });
  };

  const handleUpdateUser = async (e) => {
    e.preventDefault();
    try {
      const response = await apiService.updateUser(editingUserId, editUser);
      if (response.success) {
        setEditingUserId(null);
        fetchUsers();
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to update account: ${err.message}`);
    }
  };

  const handleDeleteUser = async (userId, name) => {
    if (!window.confirm(`Delete account "${name}"? This cannot be undone.`)) return;
    try {
      const response = await apiService.deleteUser(userId);
      if (response.success) {
        fetchUsers();
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to delete account: ${err.message}`);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <p>Manage the election, positions, candidates and voter accounts</p>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="admin-tabs">
        <button
          className={`tab-btn ${activeTab === 'elections' ? 'active' : ''}`}
          onClick={() => setActiveTab('elections')}
        >
          Election
        </button>
        <button
          className={`tab-btn ${activeTab === 'positions' ? 'active' : ''}`}
          onClick={() => setActiveTab('positions')}
        >
          Positions/Seats
        </button>
        <button
          className={`tab-btn ${activeTab === 'candidates' ? 'active' : ''}`}
          onClick={() => setActiveTab('candidates')}
        >
          Manage Candidates
        </button>
        <button
          className={`tab-btn ${activeTab === 'voters' ? 'active' : ''}`}
          onClick={() => setActiveTab('voters')}
        >
          Manage Voters
        </button>
      </div>

      {/* Election Tab */}
      {activeTab === 'elections' && (
        <div className="tab-content">
          <h2>2026 Alumni Executive Council Election</h2>
          {elections.length === 0 ? (
            <p>No election found</p>
          ) : (
            elections.map(election => (
              <div key={election._id} className="election-control-card">
                <p>
                  Status: <span className={`status-badge status-${election.status}`}>{election.status}</span>
                </p>

                <div className="election-control-actions">
                  <button
                    className="btn-action activate"
                    onClick={() => handleOpenNominations(election._id)}
                    disabled={election.status === 'draft'}
                  >
                    Allow Candidates to Select Seats
                  </button>
                  <button
                    className="btn-action activate"
                    onClick={() => handleActivateElection(election._id)}
                    disabled={election.status === 'active'}
                  >
                    Start Election
                  </button>
                  <button
                    className="btn-action close"
                    onClick={() => handleCloseElection(election._id)}
                    disabled={election.status !== 'active'}
                  >
                    Stop Election
                  </button>
                </div>

                <p className="field-hint">
                  "Allow Candidates to Select Seats" reopens seat selection for candidates (no voting yet).
                  "Start Election" locks candidate seats and opens voting.
                  "Stop Election" ends voting.
                </p>
              </div>
            ))
          )}
        </div>
      )}

      {/* Positions/Seats Tab */}
      {activeTab === 'positions' && (
        <div className="tab-content">
          <h2>Positions / Seats</h2>

          {positions.length > 0 && (
            <div className="elections-table-container mb-4">
              <table className="elections-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Region/Eligibility</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map(position => (
                    <React.Fragment key={position._id}>
                      <tr>
                        <td>{position.name}</td>
                        <td>{position.region}</td>
                        <td>
                          <button className="btn-action activate" onClick={() => startEditPosition(position)}>Edit</button>{' '}
                          <button className="btn-action close" onClick={() => handleDeletePosition(position._id, position.name)}>Delete</button>
                        </td>
                      </tr>
                      {editingPositionId === position._id && (
                        <tr>
                          <td colSpan="3">
                            <form onSubmit={handleUpdatePosition} className="candidate-form">
                              <div className="form-row">
                                <div className="form-group">
                                  <label>Name *</label>
                                  <input
                                    type="text"
                                    value={editPosition.name}
                                    onChange={(e) => setEditPosition({ ...editPosition, name: e.target.value })}
                                    required
                                  />
                                </div>
                                <div className="form-group">
                                  <label>Region/Eligibility</label>
                                  <input
                                    type="text"
                                    value={editPosition.region}
                                    onChange={(e) => setEditPosition({ ...editPosition, region: e.target.value })}
                                    placeholder="e.g., East Region"
                                  />
                                </div>
                              </div>
                              <div className="form-group">
                                <label>Description</label>
                                <textarea
                                  value={editPosition.description}
                                  onChange={(e) => setEditPosition({ ...editPosition, description: e.target.value })}
                                  rows="2"
                                ></textarea>
                              </div>
                              <button type="submit" className="btn btn-primary">Save Changes</button>{' '}
                              <button type="button" className="btn btn-secondary" onClick={() => setEditingPositionId(null)}>Cancel</button>
                            </form>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <h3>Add Position/Seat</h3>
          <form onSubmit={handleCreatePosition} className="candidate-form">
            <div className="form-row">
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={newPosition.name}
                  onChange={(e) => setNewPosition({ ...newPosition, name: e.target.value })}
                  placeholder="e.g., President, VP East Region"
                  required
                />
              </div>
              <div className="form-group">
                <label>Region/Eligibility</label>
                <input
                  type="text"
                  value={newPosition.region}
                  onChange={(e) => setNewPosition({ ...newPosition, region: e.target.value })}
                  placeholder="e.g., East Region"
                />
              </div>
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={newPosition.description}
                onChange={(e) => setNewPosition({ ...newPosition, description: e.target.value })}
                rows="2"
              ></textarea>
            </div>
            <button type="submit" className="btn btn-primary">Add Position</button>
          </form>
        </div>
      )}

      {/* Manage Candidates Tab */}
      {activeTab === 'candidates' && (
        <div className="tab-content">
          <h2>Candidates</h2>

          {candidates.length > 0 && (
            <div className="elections-table-container mb-4">
              <table className="elections-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Positions</th>
                    <th>Votes</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {candidates.map(candidate => (
                    <React.Fragment key={candidate._id}>
                      <tr>
                        <td>{candidate.name}</td>
                        <td>{(candidate.positions || []).join(', ')}</td>
                        <td>{candidate.vote_count}</td>
                        <td>
                          <button
                            className="btn-action activate"
                            onClick={() => startEditCandidate(candidate)}
                          >
                            Edit
                          </button>{' '}
                          <button
                            className="btn-action close"
                            onClick={() => handleDeleteCandidate(candidate._id, candidate.name)}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                      {editingCandidateId === candidate._id && (
                        <tr>
                          <td colSpan="4">
                            <form onSubmit={handleUpdateCandidate} className="candidate-form">
                              <div className="form-row">
                                <div className="form-group">
                                  <label>Name *</label>
                                  <input
                                    type="text"
                                    value={editCandidate.name}
                                    onChange={(e) => setEditCandidate({ ...editCandidate, name: e.target.value })}
                                    required
                                  />
                                </div>
                                <div className="form-group">
                                  <label>Positions * (max {MAX_POSITIONS_PER_CANDIDATE})</label>
                                  <PositionCheckboxes
                                    availablePositions={positions}
                                    selected={editCandidate.positions}
                                    onChange={(positions) => setEditCandidate({ ...editCandidate, positions })}
                                  />
                                  <p className="field-hint">
                                    Only admins can change which positions a candidate runs for.
                                  </p>
                                </div>
                              </div>
                              <div className="form-group">
                                <label>Bio *</label>
                                <textarea
                                  value={editCandidate.bio}
                                  onChange={(e) => setEditCandidate({ ...editCandidate, bio: e.target.value })}
                                  rows="3"
                                  required
                                ></textarea>
                              </div>
                              <div className="form-row">
                                <div className="form-group">
                                  <label>Batch Year</label>
                                  <input
                                    type="number"
                                    value={editCandidate.batch_year}
                                    onChange={(e) => setEditCandidate({ ...editCandidate, batch_year: e.target.value })}
                                  />
                                </div>
                                <div className="form-group">
                                  <label>Department</label>
                                  <input
                                    type="text"
                                    value={editCandidate.department}
                                    onChange={(e) => setEditCandidate({ ...editCandidate, department: e.target.value })}
                                  />
                                </div>
                              </div>
                              <div className="form-row">
                                <div className="form-group">
                                  <label>Email</label>
                                  <input
                                    type="email"
                                    value={editCandidate.contact_email}
                                    onChange={(e) => setEditCandidate({ ...editCandidate, contact_email: e.target.value })}
                                  />
                                </div>
                                <div className="form-group">
                                  <label>Image URL</label>
                                  <input
                                    type="url"
                                    value={editCandidate.image_url}
                                    onChange={(e) => setEditCandidate({ ...editCandidate, image_url: e.target.value })}
                                  />
                                </div>
                              </div>
                              <div className="form-group">
                                <label>Platform/Vision</label>
                                <textarea
                                  value={editCandidate.platform}
                                  onChange={(e) => setEditCandidate({ ...editCandidate, platform: e.target.value })}
                                  rows="3"
                                ></textarea>
                              </div>
                              <div className="form-row">
                                <div className="form-group">
                                  <label>LinkedIn URL</label>
                                  <input
                                    type="url"
                                    value={editCandidate.linkedin_url}
                                    onChange={(e) => setEditCandidate({ ...editCandidate, linkedin_url: e.target.value })}
                                    placeholder="https://linkedin.com/in/..."
                                  />
                                </div>
                                <div className="form-group">
                                  <label>Other Social Media URL</label>
                                  <input
                                    type="url"
                                    value={editCandidate.social_url}
                                    onChange={(e) => setEditCandidate({ ...editCandidate, social_url: e.target.value })}
                                  />
                                </div>
                              </div>
                              <button type="submit" className="btn btn-primary">Save Changes</button>{' '}
                              <button type="button" className="btn btn-secondary" onClick={() => setEditingCandidateId(null)}>Cancel</button>
                            </form>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <p className="field-hint">
            To add a new candidate, create their account from the Manage Voters tab with role
            "Candidate" - their profile is created automatically and appears here for you to
            assign seats or make corrections.
          </p>
        </div>
      )}

      {/* Manage Voters Tab */}
      {activeTab === 'voters' && (
        <div className="tab-content">
          <h2>Accounts</h2>

          {users.length > 0 && (
            <div className="elections-table-container mb-4">
              <table className="elections-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <React.Fragment key={u._id}>
                      <tr>
                        <td>{u.name}</td>
                        <td>{u.email}</td>
                        <td>{u.role}</td>
                        <td>
                          <button className="btn-action activate" onClick={() => startEditUser(u)}>Edit</button>{' '}
                          <button className="btn-action close" onClick={() => handleDeleteUser(u._id, u.name)}>Delete</button>
                        </td>
                      </tr>
                      {editingUserId === u._id && (
                        <tr>
                          <td colSpan="4">
                            <form onSubmit={handleUpdateUser} className="candidate-form">
                              <div className="form-row">
                                <div className="form-group">
                                  <label>Name</label>
                                  <input
                                    type="text"
                                    value={editUser.name}
                                    onChange={(e) => setEditUser({ ...editUser, name: e.target.value })}
                                    required
                                  />
                                </div>
                                <div className="form-group">
                                  <label>Email</label>
                                  <input
                                    type="email"
                                    value={editUser.email}
                                    onChange={(e) => setEditUser({ ...editUser, email: e.target.value })}
                                    required
                                  />
                                </div>
                              </div>
                              <div className="form-group">
                                <label>Role</label>
                                <select
                                  value={editUser.role}
                                  onChange={(e) => setEditUser({ ...editUser, role: e.target.value })}
                                >
                                  <option value="voter">Voter</option>
                                  <option value="candidate">Candidate</option>
                                  <option value="admin">Admin</option>
                                </select>
                              </div>
                              <button type="submit" className="btn btn-primary">Save Changes</button>{' '}
                              <button type="button" className="btn btn-secondary" onClick={() => setEditingUserId(null)}>Cancel</button>
                            </form>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <h3>Add Account</h3>
          <form onSubmit={handleCreateVoter} className="candidate-form">
            <div className="form-row">
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={newVoter.name}
                  onChange={(e) => setNewVoter({ ...newVoter, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={newVoter.email}
                  onChange={(e) => setNewVoter({ ...newVoter, email: e.target.value })}
                  required
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Password *</label>
                <input
                  type="password"
                  value={newVoter.password}
                  onChange={(e) => setNewVoter({ ...newVoter, password: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Role</label>
                <select
                  value={newVoter.role}
                  onChange={(e) => setNewVoter({ ...newVoter, role: e.target.value })}
                >
                  <option value="voter">Voter</option>
                  <option value="candidate">Candidate</option>
                </select>
              </div>
            </div>
            <button type="submit" className="btn btn-primary">Create Account</button>
          </form>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
