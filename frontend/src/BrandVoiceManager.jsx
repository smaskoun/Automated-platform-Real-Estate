// src/BrandVoiceManager.jsx - FINAL VERSION

import React, { useState, useEffect } from 'react';
import styles from './BrandVoiceManager.module.css';
import axios from 'axios';

// Use the environment variable for the API base URL.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function BrandVoiceManager({ user }) {
  const [voices, setVoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [newVoiceName, setNewVoiceName] = useState('');
  const [newVoiceDesc, setNewVoiceDesc] = useState('');

  // This function now fetches REAL Brand Voices.
  const fetchVoices = async () => {
    setIsLoading(true);
    setError('');
    try {
      // Use the correct endpoint we defined in the new main.py: /api/brand-voices
      const response = await axios.get(`${API_BASE_URL}/brand-voices`, {
        // We will pass the mock user's ID to fetch their voices
        params: { user_id: user.id }
      });
      // Assuming the backend returns an object like { "brand_voices": [...] }
      setVoices(response.data.brand_voices || []);
    } catch (err) {
      setError('Failed to fetch brand voices. Please ensure the backend is running and the API is correct.');
      console.error("Fetch error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch voices when the component loads.
  useEffect(() => {
    if (user && user.id) {
      fetchVoices();
    }
  }, [user]);

  // This function now CREATES a real Brand Voice.
  const handleCreateVoice = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/brand-voices`, {
        user_id: user.id,
        name: newVoiceName,
        description: newVoiceDesc,
      });
      setNewVoiceName('');
      setNewVoiceDesc('');
      fetchVoices(); // Refresh the list.
    } catch (err) {
      console.error("Create error:", err);
      alert("Failed to create brand voice.");
    }
  };

  // This function now DELETES a real Brand Voice.
  const handleDeleteVoice = async (voiceId) => {
    if (window.confirm("Are you sure you want to delete this brand voice?")) {
      try {
        await axios.delete(`${API_BASE_URL}/brand-voices/${voiceId}`);
        fetchVoices(); // Refresh the list.
      } catch (err) {
        console.error("Delete error:", err);
        alert("Failed to delete brand voice.");
      }
    }
  };

  if (isLoading) {
    return <div className={styles.loading}>Loading brand voices...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  return (
    <div className={styles.manager}>
      <div className={styles.formCard}>
        <h3>Create New Brand Voice</h3>
        <form onSubmit={handleCreateVoice}>
          <input
            type="text"
            placeholder="Brand Voice Name (e.g., 'Professional & Witty')"
            value={newVoiceName}
            onChange={(e) => setNewVoiceName(e.target.value)}
            required
          />
          <textarea
            placeholder="Describe the brand voice... (e.g., 'Uses clear, concise language...')"
            value={newVoiceDesc}
            onChange={(e) => setNewVoiceDesc(e.target.value)}
            required
          />
          <button type="submit">Create Voice</button>
        </form>
      </div>

      <div className={styles.listCard}>
        <h3>Your Brand Voices</h3>
        {voices.length > 0 ? (
          <ul className={styles.voiceList}>
            {voices.map((voice) => (
              <li key={voice.id} className={styles.voiceItem}>
                <div className={styles.voiceInfo}>
                  <strong>{voice.name}</strong>
                  <p>{voice.description}</p>
                </div>
                <div className={styles.voiceActions}>
                  <button onClick={() => handleDeleteVoice(voice.id)} className={styles.deleteButton}>Delete</button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>You haven't created any brand voices yet. Use the form above to get started.</p>
        )}
      </div>
    </div>
  );
}

export default BrandVoiceManager;
