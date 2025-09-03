import React, { useState, useEffect } from 'react';
import styles from './BrandVoiceManager.module.css';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://your-backend-app.onrender.com';

function BrandVoiceManager({ user } ) {
  const [voices, setVoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [newVoiceName, setNewVoiceName] = useState('');
  const [newVoiceDesc, setNewVoiceDesc] = useState('');

  // Function to fetch brand voices
  const fetchVoices = async () => {
    setIsLoading(true);
    setError('');
    try {
      // --- THIS IS THE CORRECTED LINE ---
      // We now pass the user.id as a query parameter
      const response = await axios.get(`${API_URL}/brand-voices`, {
        params: { user_id: user.id }
      });
      setVoices(response.data.brand_voices || []);
    } catch (err) {
      setError('Failed to fetch brand voices. Please try again later.');
      console.error("Fetch error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch voices when the component loads
  useEffect(() => {
    if (user && user.id) {
      fetchVoices();
    }
  }, [user]);

  // Handle form submission for new brand voice
  const handleCreateVoice = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/brand-voices`, {
        user_id: user.id,
        name: newVoiceName,
        description: newVoiceDesc,
      });
      if (response.data.success) {
        setNewVoiceName('');
        setNewVoiceDesc('');
        fetchVoices(); // Refresh the list after creating
      }
    } catch (err) {
      console.error("Create error:", err);
      alert("Failed to create brand voice.");
    }
  };

  // Handle deleting a brand voice
  const handleDeleteVoice = async (voiceId) => {
    if (window.confirm("Are you sure you want to delete this brand voice?")) {
      try {
        await axios.delete(`${API_URL}/brand-voices/${voiceId}`);
        fetchVoices(); // Refresh the list after deleting
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
            placeholder="Describe the brand voice... (e.g., 'Uses clear, concise language with a touch of humor. Avoids jargon.')"
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
