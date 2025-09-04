// frontend/src/BrandVoiceManager.jsx - NEW VERSION

import React, { useState, useEffect } from 'react';
import styles from './BrandVoiceManager.module.css';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function BrandVoiceManager({ user }) {
  const [voices, setVoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [newVoiceName, setNewVoiceName] = useState('');
  const [newVoiceDesc, setNewVoiceDesc] = useState('');
  // NEW STATE: To hold the content of the example post
  const [newPostExample, setNewPostExample] = useState('');

  const fetchVoices = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_BASE_URL}/brand-voices/`, {
        params: { user_id: user.id }
      });
      setVoices(response.data.brand_voices || []);
    } catch (err) {
      setError('Failed to fetch brand voices. Please ensure the backend is running and the API is correct.');
      console.error("Fetch error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (user && user.id) {
      fetchVoices();
    }
  }, [user]);

  const handleCreateVoice = async (e) => {
    e.preventDefault();
    try {
      // UPDATED: Send the new 'post_example' field to the backend
      await axios.post(`${API_BASE_URL}/brand-voices/`, {
        user_id: user.id,
        name: newVoiceName,
        description: newVoiceDesc,
        post_example: newPostExample,
      });
      // Reset all form fields
      setNewVoiceName('');
      setNewVoiceDesc('');
      setNewPostExample('');
      fetchVoices();
    } catch (err) {
      console.error("Create error:", err);
      alert("Failed to create source content.");
    }
  };

  const handleDeleteVoice = async (voiceId) => {
    if (window.confirm("Are you sure you want to delete this source content?")) {
      try {
        await axios.delete(`${API_BASE_URL}/brand-voices/${voiceId}/`);
        fetchVoices();
      } catch (err) {
        console.error("Delete error:", err);
        alert("Failed to delete source content.");
      }
    }
  };

  if (isLoading) {
    return <div className={styles.loading}>Loading Source Content...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  return (
    <div className={styles.manager}>
      <div className={styles.formCard}>
        <h3>Add New Source Content</h3>
        <form onSubmit={handleCreateVoice}>
          <input
            type="text"
            placeholder="Content Title (e.g., 'Just Listed - 123 Main St')"
            value={newVoiceName}
            onChange={(e) => setNewVoiceName(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Short Description (e.g., 'Successful post from May 2024')"
            value={newVoiceDesc}
            onChange={(e) => setNewVoiceDesc(e.target.value)}
            required
          />
          {/* NEW TEXTAREA: For pasting the full post content */}
          <textarea
            placeholder="Paste the full content of your successful post here..."
            value={newPostExample}
            onChange={(e) => setNewPostExample(e.target.value)}
            required
            rows="8"
          />
          <button type="submit">Add Content</button>
        </form>
      </div>

      <div className={styles.listCard}>
        <h3>Your Source Content Library</h3>
        {voices.length > 0 ? (
          <ul className={styles.voiceList}>
            {voices.map((voice) => (
              <li key={voice.id} className={styles.voiceItem}>
                <div className={styles.voiceInfo}>
                  <strong>{voice.name}</strong>
                  <p>{voice.description}</p>
                  {/* UPDATED: Display the example post content */}
                  <pre className={styles.postExample}>{voice.post_example}</pre>
                </div>
                <div className={styles.voiceActions}>
                  <button onClick={() => handleDeleteVoice(voice.id)} className={styles.deleteButton}>Delete</button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>You haven't added any source content yet. Use the form above to get started.</p>
        )}
      </div>
    </div>
  );
}

export default BrandVoiceManager;
