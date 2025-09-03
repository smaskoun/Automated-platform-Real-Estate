// src/BrandVoiceManager.jsx - NEW CORRECTED CODE

import React, { useState, useEffect } from 'react';
import styles from './BrandVoiceManager.module.css';
import axios from 'axios';

// Use the environment variable we created for the API base URL.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function BrandVoiceManager({ user }) {
  // Renamed 'voices' to 'items' for clarity. This will hold the list of users.
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [newItemName, setNewItemName] = useState('');
  const [newItemDesc, setNewItemDesc] = useState('');

  // This function now fetches USERS from your real backend.
  const fetchItems = async () => {
    setIsLoading(true);
    setError('');
    try {
      // Use the correct endpoint from your backend: /users
      const response = await axios.get(`${API_BASE_URL}/users`);
      setItems(response.data || []);
    } catch (err) {
      setError('Failed to fetch data. Please check the backend connection and CORS settings.');
      console.error("Fetch error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch the data when the component first loads.
  useEffect(() => {
    fetchItems();
  }, []);

  // This function now CREATES a new USER.
  const handleCreateItem = async (e) => {
    e.preventDefault();
    try {
      // Use the correct endpoint and field names for creating a user.
      await axios.post(`${API_BASE_URL}/users`, {
        username: newItemName,
        email: newItemDesc, // We use the description field as the email for this test.
      });
      setNewItemName('');
      setNewItemDesc('');
      fetchItems(); // Refresh the list to show the new user.
    } catch (err) {
      console.error("Create error:", err);
      alert("Failed to create user. The username or email might already exist.");
    }
  };

  // This function now DELETES a USER.
  const handleDeleteItem = async (itemId) => {
    if (window.confirm("Are you sure you want to delete this user?")) {
      try {
        // Use the correct endpoint for deleting a user.
        await axios.delete(`${API_BASE_URL}/users/${itemId}`);
        fetchItems(); // Refresh the list.
      } catch (err) {
        console.error("Delete error:", err);
        alert("Failed to delete user.");
      }
    }
  };

  if (isLoading) {
    return <div className={styles.loading}>Loading data from backend...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  return (
    <div className={styles.manager}>
      <div className={styles.formCard}>
        <h3>Create New User</h3>
        <form onSubmit={handleCreateItem}>
          <input
            type="text"
            placeholder="Username"
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            required
          />
          <textarea
            placeholder="Email"
            value={newItemDesc}
            onChange={(e) => setNewItemDesc(e.target.value)}
            required
          />
          <button type="submit">Create User</button>
        </form>
      </div>

      <div className={styles.listCard}>
        <h3>Existing Users</h3>
        {items.length > 0 ? (
          <ul className={styles.voiceList}>
            {items.map((item) => (
              <li key={item.id} className={styles.voiceItem}>
                <div className={styles.voiceInfo}>
                  {/* Use the actual fields from your user model: username and email */}
                  <strong>{item.username}</strong>
                  <p>{item.email}</p>
                </div>
                <div className={styles.voiceActions}>
                  <button onClick={() => handleDeleteItem(item.id)} className={styles.deleteButton}>Delete</button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>No users found. Use the form above to create one.</p>
        )}
      </div>
    </div>
  );
}

export default BrandVoiceManager;
