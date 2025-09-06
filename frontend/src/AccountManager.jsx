// frontend/src/components/AccountManager.jsx - FULL REPLACEMENT (with Edit/Delete)

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styles from './AccountManager.module.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function AccountManager({ user }) {
  const [accounts, setAccounts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Form state for adding
  const [accountName, setAccountName] = useState('');
  const [platform, setPlatform] = useState('Facebook');

  // State for editing
  const [editingAccount, setEditingAccount] = useState(null); // Holds the account being edited
  const [editName, setEditName] = useState('');
  const [editPlatform, setEditPlatform] = useState('');

  const fetchAccounts = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/social-media/social-accounts`, {
        params: { user_id: user.id }
      });
      setAccounts(response.data.accounts || []);
    } catch (err) {
      setError('Failed to fetch accounts.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (user?.id) {
      fetchAccounts();
    }
  }, [user]);

  const handleAddAccount = async (e) => {
    e.preventDefault();
    if (!accountName || !platform) {
      alert('Please provide an account name and select a platform.');
      return;
    }
    try {
      await axios.post(`${API_BASE_URL}/social-media/social-accounts`, {
        user_id: user.id,
        account_name: accountName,
        platform: platform,
      });
      setAccountName('');
      fetchAccounts();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to add account.');
    }
  };

  // --- NEW: Function to handle deleting an account ---
  const handleDeleteAccount = async (accountId) => {
    if (window.confirm("Are you sure you want to delete this account? All associated posts will also be deleted.")) {
      try {
        await axios.delete(`${API_BASE_URL}/social-media/social-accounts/${accountId}`);
        fetchAccounts(); // Refresh the list
      } catch (err) {
        alert('Failed to delete account.');
      }
    }
  };

  // --- NEW: Function to start editing an account ---
  const handleStartEdit = (account) => {
    setEditingAccount(account);
    setEditName(account.account_name);
    setEditPlatform(account.platform);
  };

  // --- NEW: Function to cancel editing ---
  const handleCancelEdit = () => {
    setEditingAccount(null);
  };

  // --- NEW: Function to save the edited account ---
  const handleSaveEdit = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${API_BASE_URL}/social-media/social-accounts/${editingAccount.id}`, {
        account_name: editName,
        platform: editPlatform,
      });
      setEditingAccount(null); // Close the edit form
      fetchAccounts(); // Refresh the list
    } catch (err) {
      alert('Failed to save changes.');
    }
  };

  return (
    <div className={styles.container}>
      {/* --- NEW: Edit Modal --- */}
      {editingAccount && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <h3>Edit Account</h3>
            <form onSubmit={handleSaveEdit}>
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                required
              />
              <select value={editPlatform} onChange={(e) => setEditPlatform(e.target.value)}>
                <option value="Facebook">Facebook</option>
                <option value="Instagram">Instagram</option>
                <option value="Google Business Profile">Google Business Profile</option>
              </select>
              <div className={styles.modalActions}>
                <button type="button" onClick={handleCancelEdit} className={styles.cancelButton}>Cancel</button>
                <button type="submit">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className={styles.card}>
        <h3>Add New Account</h3>
        <form onSubmit={handleAddAccount} className={styles.form}>
          <input
            type="text"
            value={accountName}
            onChange={(e) => setAccountName(e.target.value)}
            placeholder="e.g., My Main Facebook Page"
            required
          />
          <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
            <option value="Facebook">Facebook</option>
            <option value="Instagram">Instagram</option>
            <option value="Google Business Profile">Google Business Profile</option>
          </select>
          <button type="submit">Add Account</button>
        </form>
      </div>

      <div className={styles.card}>
        <h3>Your Accounts</h3>
        {isLoading ? (
          <p>Loading accounts...</p>
        ) : error ? (
          <p className={styles.error}>{error}</p>
        ) : (
          <ul className={styles.accountList}>
            {accounts.length > 0 ? (
              accounts.map(acc => (
                <li key={acc.id}>
                  <div className={styles.accountInfo}>
                    <span>{acc.account_name}</span>
                    <span className={`${styles.platform} ${styles[acc.platform.toLowerCase().replace(/\s+/g, '')]}`}>
                      {acc.platform}
                    </span>
                  </div>
                  {/* --- NEW: Edit and Delete Buttons --- */}
                  <div className={styles.accountActions}>
                    <button onClick={() => handleStartEdit(acc)} className={styles.editButton}>Edit</button>
                    <button onClick={() => handleDeleteAccount(acc.id)} className={styles.deleteButton}>Delete</button>
                  </div>
                </li>
              ))
            ) : (
              <p>No accounts found. Add one using the form above.</p>
            )}
          </ul>
        )}
      </div>
    </div>
  );
}

export default AccountManager;
