import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/CandidateProfile.css';

const readFileAsBase64 = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.onload = () => resolve(reader.result);
  reader.onerror = reject;
  reader.readAsDataURL(file);
});

const MAX_POSITIONS_PER_CANDIDATE = 3;

const CandidateProfile = () => {
  const [candidate, setCandidate] = useState(null);
  const [form, setForm] = useState({ image_url: '', bio: '', linkedin_url: '', social_url: '' });
  const [positions, setPositions] = useState([]);
  const [selectedPositions, setSelectedPositions] = useState([]);
  const [campaignMedia, setCampaignMedia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notLinked, setNotLinked] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [saving, setSaving] = useState(false);
  const [savingPositions, setSavingPositions] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadingMedia, setUploadingMedia] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await apiService.getMyCandidateProfile();
      if (response.success) {
        setCandidate(response.candidate);
        setForm({
          image_url: response.candidate.image_url || '',
          bio: response.candidate.bio || '',
          linkedin_url: response.candidate.linkedin_url || '',
          social_url: response.candidate.social_url || ''
        });
        setSelectedPositions(response.candidate.positions || []);
        setCampaignMedia(response.candidate.campaign_media || []);
        setNotLinked(false);

        if (response.candidate.election_id) {
          const positionsResponse = await apiService.getPositions(response.candidate.election_id);
          setPositions(positionsResponse.positions || []);
        }
      } else {
        setNotLinked(true);
      }
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const seatsLocked = candidate?.election_status && candidate.election_status !== 'draft';

  const togglePosition = (name) => {
    if (seatsLocked) return;
    setSelectedPositions(prev => {
      if (prev.includes(name)) {
        return prev.filter(p => p !== name);
      }
      if (prev.length >= MAX_POSITIONS_PER_CANDIDATE) {
        setError(`You can run for at most ${MAX_POSITIONS_PER_CANDIDATE} positions`);
        return prev;
      }
      return [...prev, name];
    });
  };

  const handleSavePositions = async () => {
    setMessage(null);
    setError(null);
    setSavingPositions(true);
    try {
      const response = await apiService.updateMyCandidateProfile({ positions: selectedPositions });
      if (response.success) {
        setMessage('Seats saved successfully');
        fetchProfile();
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingPositions(false);
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handlePhotoSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      setError('Image must be smaller than 5MB');
      return;
    }

    setMessage(null);
    setError(null);
    setUploading(true);
    try {
      const base64 = await readFileAsBase64(file);
      const response = await apiService.uploadMyCandidatePhoto(base64, file.type);
      if (response.success) {
        setForm(prev => ({ ...prev, image_url: response.image_url }));
        setMessage('Photo uploaded successfully');
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleMediaSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const isVideo = file.type.startsWith('video/');
    const maxSize = isVideo ? 20 * 1024 * 1024 : 5 * 1024 * 1024;
    if (file.size > maxSize) {
      setError(`File must be smaller than ${maxSize / (1024 * 1024)}MB`);
      return;
    }

    setMessage(null);
    setError(null);
    setUploadingMedia(true);
    try {
      const base64 = await readFileAsBase64(file);
      const response = await apiService.uploadMyCampaignMedia(base64, file.type);
      if (response.success) {
        setCampaignMedia(prev => [...prev, response.media]);
        setMessage('Campaign media uploaded successfully');
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setUploadingMedia(false);
      e.target.value = '';
    }
  };

  const handleDeleteMedia = async (url) => {
    if (!window.confirm('Remove this campaign media item?')) return;
    try {
      const response = await apiService.deleteMyCampaignMedia(url);
      if (response.success) {
        setCampaignMedia(prev => prev.filter(m => m.url !== url));
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    setSaving(true);
    try {
      const response = await apiService.updateMyCandidateProfile(form);
      if (response.success) {
        setMessage('Profile updated successfully');
        fetchProfile();
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  if (notLinked) {
    return (
      <div className="candidate-profile-container">
        <div className="warning-message">
          We couldn't set up your candidate profile automatically. Please log out and log back in
          to try again, or contact an admin if this keeps happening.
        </div>
      </div>
    );
  }

  return (
    <div className="candidate-profile-container">
      <div className="candidate-profile-header">
        <h1>My Candidate Profile</h1>
        <p>{candidate?.name} &middot; {(candidate?.positions || []).join(', ') || 'No seats selected yet'}</p>
      </div>

      {error && <div className="error-message">{error}</div>}
      {message && <div className="success-message">{message}</div>}

      <div className="candidate-profile-header mt-4">
        <h2>Seats I'm Running For</h2>
        <p>Select up to {MAX_POSITIONS_PER_CANDIDATE} seats. Once the election opens, only an admin can change your seats.</p>
      </div>

      <div className="form-group">
        {seatsLocked && (
          <p className="field-hint">
            Seats are locked because the election is {candidate.election_status}. Contact an admin to change them.
          </p>
        )}

        {positions.length === 0 ? (
          <p className="field-hint">No seats have been set up by the admin yet.</p>
        ) : (
          <div className="position-checkbox-group">
            {positions.map(p => (
              <label key={p._id} className="position-checkbox">
                <input
                  type="checkbox"
                  checked={selectedPositions.includes(p.name)}
                  onChange={() => togglePosition(p.name)}
                  disabled={seatsLocked}
                />
                {p.name}{p.region ? ` (${p.region})` : ''}
              </label>
            ))}
          </div>
        )}

        {!seatsLocked && positions.length > 0 && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleSavePositions}
            disabled={savingPositions}
          >
            {savingPositions ? 'Saving...' : 'Save Seats'}
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="candidate-profile-form">
        <div className="form-group">
          <label>Photo</label>
          <input
            type="file"
            accept="image/*"
            onChange={handlePhotoSelect}
            disabled={uploading}
          />
          {uploading && <p className="field-hint">Uploading...</p>}
          {form.image_url && (
            <img src={form.image_url} alt="Preview" className="profile-photo-preview" />
          )}
        </div>

        <div className="form-group">
          <label>Profile Text (Bio)</label>
          <textarea
            name="bio"
            value={form.bio}
            onChange={handleChange}
            rows="5"
            required
          ></textarea>
        </div>

        <div className="form-group">
          <label>LinkedIn URL</label>
          <input
            type="url"
            name="linkedin_url"
            value={form.linkedin_url}
            onChange={handleChange}
            placeholder="https://linkedin.com/in/..."
          />
        </div>

        <div className="form-group">
          <label>Other Social Media URL</label>
          <input
            type="url"
            name="social_url"
            value={form.social_url}
            onChange={handleChange}
            placeholder="https://facebook.com/... or https://x.com/..."
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>

      <div className="candidate-profile-header mt-4">
        <h2>Election Campaign Media</h2>
        <p>Upload campaign photos or videos for voters to see on your profile.</p>
      </div>

      <div className="form-group">
        <input
          type="file"
          accept="image/*,video/*"
          onChange={handleMediaSelect}
          disabled={uploadingMedia}
        />
        {uploadingMedia && <p className="field-hint">Uploading...</p>}
      </div>

      {campaignMedia.length > 0 && (
        <div className="campaign-media-grid">
          {campaignMedia.map((item) => (
            <div key={item.url} className="campaign-media-item">
              {item.media_type === 'video' ? (
                <video src={item.url} controls />
              ) : (
                <img src={item.url} alt="Campaign media" />
              )}
              <button
                type="button"
                className="btn-action close"
                onClick={() => handleDeleteMedia(item.url)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CandidateProfile;
