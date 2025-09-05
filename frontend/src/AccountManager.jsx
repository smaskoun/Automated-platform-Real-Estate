// frontend/src/components/AccountManager.jsx (NEW FILE)

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styles from './AccountManager.module.css'; // We will create this CSS file next

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function AccountManager({ user }) {
  const [accounts, setAccounts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Form state
  const [accountName, setAccountName] = useState('');
  const [platform, setPlatform] = useState('Facebook'); // Default platform

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
      setAccountName(''); // Reset form
      fetchAccounts(); // Refresh the list
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to add account.');
      console.error(err);
    }
  };

  return (
    <div className={styles.container}>
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
                  <span>{acc.account_name}</span>
                  <span className={`${styles.platform} ${styles[acc.platform.toLowerCase().replace(/\s+/g, '')]}`}>
                    {acc.platform}
                  </span>
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
