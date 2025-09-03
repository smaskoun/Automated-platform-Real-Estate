import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styles from './BrandVoiceManager.module.css';

// IMPORTANT: Replace this with your actual backend URL from Render
const API_URL = 'https://your-backend-app.onrender.com';

function BrandVoiceManager({ user } ) {
  const [brandVoices, setBrandVoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // State for the "Create New" form
  const [newName, setNewName] = useState('');
  const [newDescription, setNewDescription] = useState('');

  // --- API Functions ---

  // 1. Fetch all brand voices for the current user
  const fetchBrandVoices = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_URL}/brand-voices`, {
        params: { user_id: user.id }
      });
      setBrandVoices(response.data.brand_voices);
    } catch (err) {
      setError('Failed to fetch brand voices. Please try again later.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // 2. Create a new brand voice
  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/brand-voices`, {
        user_id: user.id,
        name: newName,
        description: newDescription,
      });
      if (response.data.success) {
        fetchBrandVoices(); // Refresh the list
        setNewName('');
        setNewDescription('');
      }
    } catch (err) {
      setError('Failed to create brand voice.');
      console.error(err);
    }
  };

  // 3. Delete a brand voice
  const handleDelete = async (voiceId) => {
    if (window.confirm('Are you sure you want to delete this brand voice?')) {
      try {
        await axios.delete(`${API_URL}/brand-voices/${voiceId}`);
        fetchBrandVoices(); // Refresh the list
      } catch (err) {
        setError('Failed to delete brand voice.');
        console.error(err);
      }
    }
  };

  // --- useEffect Hook ---
  // This runs once when the component is first loaded
  useEffect(() => {
    fetchBrandVoices();
  }, [user.id]); // Re-run if the user ID ever changes

  // --- Render Logic ---

  if (isLoading) {
    return <div className={styles.loading}>Loading Brand Voices...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  return (
    <div className={styles.manager}>
      {/* Create New Brand Voice Form */}
      <div className={styles.formCard}>
        <h3>Create a New Brand Voice</h3>
        <form onSubmit={handleCreate}>
          <input
            type="text"
            placeholder="Brand Voice Name (e.g., 'Friendly & Professional')"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            required
          />
          <textarea
            placeholder="Description (e.g., 'Uses clear language, avoids jargon, includes emojis.')"
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            required
          />
          <button type="submit">Create</button>
        </form>
      </div>

      {/* List of Existing Brand Voices */}
      <div className={styles.listCard}>
        <h3>Your Brand Voices</h3>
        {brandVoices.length === 0 ? (
          <p>You haven't created any brand voices yet.</p>
        ) : (
          <ul className={styles.voiceList}>
            {brandVoices.map((voice) => (
              <li key={voice.id} className={styles.voiceItem}>
                <div className={styles.voiceInfo}>
                  <strong>{voice.name}</strong>
                  <p>{voice.description}</p>
                </div>
                <div className={styles.voiceActions}>
                  {/* We will add Edit and Generate buttons later */}
                  <button onClick={() => handleDelete(voice.id)} className={styles.deleteButton}>Delete</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default BrandVoiceManager;
