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

  closeElection: async (electionId) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/close`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      }
    });
    if (!response.ok) throw new Error('Failed to close election');
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

  addCandidate: async (electionId, data) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/candidates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to add candidate');
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
  
  castVote: async (electionId, candidateId) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/vote`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ candidate_id: candidateId })
    });
    if (!response.ok) throw new Error('Failed to cast vote');
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

  getPositionResults: async (electionId, position) => {
    const response = await fetch(`${API_BASE_URL}/elections/${electionId}/results/${position}`, {
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch position results');
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
