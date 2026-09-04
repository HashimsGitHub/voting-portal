const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const apiService = {
  // ==================== ELECTIONS ====================
  
  getElections: async (status = null) => {
    const url = status ? `${API_BASE_URL}/elections?status=${status}` : `${API_BASE_URL}/elections`;
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch elections');
    return response.json();
  },

  getElectionDetails: async (electionId) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}`, {
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch election details');
    return response.json();
  },

  createElection: async (data) => {
    const response = await fetch(`${API_BASE_URL}/elections`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create election');
    return response.json();
  },

  updateElection: async (electionId, data) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update election');
    return response.json();
  },

  openNominations: async (electionId) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/open-nominations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      }
    });
    return response.json();
  },

  activateElection: async (electionId) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/activate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      }
    });
    if (!response.ok) throw new Error('Failed to activate election');
    return response.json();
  },

  closeElection: async (electionId, force = false) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/close`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ force })
    });
    return response.json();
  },

  // ==================== CANDIDATES ====================
  
  getCandidates: async (electionId, position = null) => {
    const url = position 
      ? `${API_BASE_URL}/elections/${electionId}/candidates?position=${position}`
      : `${API_BASE_URL}/elections/${electionId}/candidates`;
    
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch candidates');
    return response.json();
  },

  updateCandidate: async (candidateId, data) => {
    const response = await fetch(`${API_BASE_URL}/candidates/${candidateId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  deleteCandidate: async (candidateId) => {
    const response = await fetch(`${API_BASE_URL}/candidates/${candidateId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      }
    });
    if (!response.ok) throw new Error('Failed to delete candidate');
    return response.json();
  },

  // ==================== VOTING ====================
  
  castVote: async (electionId, candidateId, position) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/vote`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ candidate_id: candidateId, position })
    });
    return response.json();
  },

  // ==================== POSITIONS (SEATS) ====================

  getPositions: async (electionId) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/positions`, {
      headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
  },

  createPosition: async (electionId, data) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/positions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  updatePosition: async (positionId, data) => {
    const response = await fetch(`${API_BASE_URL}/positions/${positionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  deletePosition: async (positionId) => {
    const response = await fetch(`${API_BASE_URL}/positions/${positionId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() }
    });
    return response.json();
  },

  // ==================== RESULTS ====================
  
  getLiveResults: async (electionId) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/results`, {
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch results');
    return response.json();
  },

  getElectionStats: async (electionId) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/stats`, {
      headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
  },

  getPositionResults: async (electionId, position) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/results/${position}`, {
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch position results');
    return response.json();
  },

  // ==================== CANDIDATE SELF-SERVICE ====================

  getMyCandidateProfile: async () => {
    const response = await fetch(`${API_BASE_URL}/candidates/me`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      }
    });
    // Backend returns a JSON body with success:false + error even on 401/403/404 -
    // let the caller read that instead of masking it with a generic message.
    return response.json();
  },

  updateMyCandidateProfile: async (data) => {
    const response = await fetch(`${API_BASE_URL}/candidates/me`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  uploadMyCandidatePhoto: async (imageBase64, contentType) => {
    const response = await fetch(`${API_BASE_URL}/candidates/me/photo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ image_base64: imageBase64, content_type: contentType })
    });
    return response.json();
  },

  uploadMyCampaignMedia: async (mediaBase64, contentType) => {
    const response = await fetch(`${API_BASE_URL}/candidates/me/media`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ media_base64: mediaBase64, content_type: contentType })
    });
    return response.json();
  },

  deleteMyCampaignMedia: async (url) => {
    const response = await fetch(`${API_BASE_URL}/candidates/me/media`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ url })
    });
    return response.json();
  },

  // ==================== USER (VOTER) MANAGEMENT ====================

  getUsers: async (role = null) => {
    const url = role ? `${API_BASE_URL}/users?role=${role}` : `${API_BASE_URL}/users`;
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() }
    });
    return response.json();
  },

  createUser: async (data) => {
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  updateUser: async (userId, data) => {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  deleteUser: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() }
    });
    return response.json();
  },

  // ==================== AUTHENTICATION ====================
  
  login: async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!response.ok) throw new Error('Login failed');
    return response.json();
  },

  register: async (data) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Registration failed');
    return response.json();
  }
};
