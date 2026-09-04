import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/AdminDashboard.css';

const AdminDashboard = () => {
  const [elections, setElections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('elections');
  const [newElection, setNewElection] = useState({
    title: '',
    description: '',
    total_seats: 10
  });
  const [newCandidate, setNewCandidate] = useState({
    name: '',
    position: '',
    bio: '',
    image_url: '',
    batch_year: '',
    department: '',
    contact_email: '',
    platform: ''
  });
  const [selectedElection, setSelectedElection] = useState(null);

  useEffect(() => {
    fetchElections();
  }, []);

  const fetchElections = async () => {
    try {
      setLoading(true);
      const response = await apiService.getElections();
      setElections(response.elections || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching elections:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateElection = async (e) => {
    e.preventDefault();
    try {
      const response = await apiService.createElection(newElection);
      if (response.success) {
        alert('Election created successfully!');
        setNewElection({
          title: '',
          description: '',
          total_seats: 10
        });
        fetchElections();
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to create election: ${err.message}`);
    }
  };

  const handleAddCandidate = async (e) => {
    e.preventDefault();
    if (!selectedElection) {
      alert('Please select an election first');
      return;
    }

    try {
      const candidateData = {
        ...newCandidate,
        batch_year: newCandidate.batch_year ? parseInt(newCandidate.batch_year) : null
      };
      
      const response = await apiService.addCandidate(selectedElection, candidateData);
      if (response.success) {
        alert('Candidate added successfully!');
        setNewCandidate({
          name: '',
          position: '',
          bio: '',
          image_url: '',
          batch_year: '',
          department: '',
          contact_email: '',
          platform: ''
        });
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to add candidate: ${err.message}`);
    }
  };

  const handleActivateElection = async (electionId) => {
    try {
      const response = await apiService.activateElection(electionId);
      if (response.success) {
        alert('Election activated!');
        fetchElections();
      } else {
        alert(`Error: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to activate election: ${err.message}`);
    }
  };

  const handleCloseElection = async (electionId) => {
    if (window.confirm('Are you sure you want to close this election?')) {
      try {
        const response = await apiService.closeElection(electionId);
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

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <p>Manage elections and candidates</p>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="admin-tabs">
        <button
          className={`tab-btn ${activeTab === 'elections' ? 'active' : ''}`}
          onClick={() => setActiveTab('elections')}
        >
          Elections
        </button>
        <button
          className={`tab-btn ${activeTab === 'create' ? 'active' : ''}`}
          onClick={() => setActiveTab('create')}
        >
          Create Election
        </button>
        <button
          className={`tab-btn ${activeTab === 'candidates' ? 'active' : ''}`}
          onClick={() => setActiveTab('candidates')}
        >
          Manage Candidates
        </button>
      </div>

      {/* Elections Tab */}
      {activeTab === 'elections' && (
        <div className="tab-content">
          <h2>Elections</h2>
          {elections.length === 0 ? (
            <p>No elections found</p>
          ) : (
            <div className="elections-table-container">
              <table className="elections-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Seats</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {elections.map(election => (
                    <tr key={election._id}>
                      <td>{election.title}</td>
                      <td><span className={`status-badge status-${election.status}`}>{election.status}</span></td>
                      <td>{election.total_seats}</td>
                      <td>{new Date(election.created_at).toLocaleDateString()}</td>
                      <td>
                        {election.status === 'draft' && (
                          <button
                            className="btn-action activate"
                            onClick={() => handleActivateElection(election._id)}
                          >
                            Activate
                          </button>
                        )}
                        {election.status === 'active' && (
                          <button
                            className="btn-action close"
                            onClick={() => handleCloseElection(election._id)}
                          >
                            Close
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Create Election Tab */}
      {activeTab === 'create' && (
        <div className="tab-content">
          <h2>Create New Election</h2>
          <form onSubmit={handleCreateElection} className="election-form">
            <div className="form-group">
              <label>Election Title *</label>
              <input
                type="text"
                value={newElection.title}
                onChange={(e) => setNewElection({ ...newElection, title: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Description *</label>
              <textarea
                value={newElection.description}
                onChange={(e) => setNewElection({ ...newElection, description: e.target.value })}
                rows="4"
                required
              ></textarea>
            </div>

            <div className="form-group">
              <label>Total Seats</label>
              <input
                type="number"
                value={newElection.total_seats}
                onChange={(e) => setNewElection({ ...newElection, total_seats: parseInt(e.target.value) })}
                min="1"
              />
            </div>

            <button type="submit" className="btn btn-primary">
              Create Election
            </button>
          </form>
        </div>
      )}

      {/* Manage Candidates Tab */}
      {activeTab === 'candidates' && (
        <div className="tab-content">
          <h2>Add Candidates</h2>

          <div className="form-section">
            <label htmlFor="election-select">Select Election *</label>
            <select
              id="election-select"
              value={selectedElection}
              onChange={(e) => setSelectedElection(e.target.value)}
            >
              <option value="">-- Choose an election --</option>
              {elections.map(election => (
                <option key={election._id} value={election._id}>
                  {election.title}
                </option>
              ))}
            </select>
          </div>

          {selectedElection && (
            <form onSubmit={handleAddCandidate} className="candidate-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Candidate Name *</label>
                  <input
                    type="text"
                    value={newCandidate.name}
                    onChange={(e) => setNewCandidate({ ...newCandidate, name: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Position *</label>
                  <input
                    type="text"
                    value={newCandidate.position}
                    onChange={(e) => setNewCandidate({ ...newCandidate, position: e.target.value })}
                    placeholder="e.g., President, Vice President"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Bio *</label>
                <textarea
                  value={newCandidate.bio}
                  onChange={(e) => setNewCandidate({ ...newCandidate, bio: e.target.value })}
                  rows="3"
                  required
                ></textarea>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Batch Year</label>
                  <input
                    type="number"
                    value={newCandidate.batch_year}
                    onChange={(e) => setNewCandidate({ ...newCandidate, batch_year: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label>Department</label>
                  <input
                    type="text"
                    value={newCandidate.department}
                    onChange={(e) => setNewCandidate({ ...newCandidate, department: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={newCandidate.contact_email}
                    onChange={(e) => setNewCandidate({ ...newCandidate, contact_email: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label>Image URL</label>
                  <input
                    type="url"
                    value={newCandidate.image_url}
                    onChange={(e) => setNewCandidate({ ...newCandidate, image_url: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Platform/Vision</label>
                <textarea
                  value={newCandidate.platform}
                  onChange={(e) => setNewCandidate({ ...newCandidate, platform: e.target.value })}
                  rows="3"
                ></textarea>
              </div>

              <button type="submit" className="btn btn-primary">
                Add Candidate
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
