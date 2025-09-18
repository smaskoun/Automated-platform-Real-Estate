import React, { useState, useEffect } from 'react';
import api from './api.js';
import styles from './AccountManager.module.css';

function AccountManager({ user }) {
  const [accounts, setAccounts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const platformIconLabels = {
    Facebook: 'FB',
    Instagram: 'IG',
    'Google Business Profile': 'GB',
  };

  const normalizePlatform = (value = '') => {
    const trimmed = value.trim();
    if (!trimmed) return '';

    const normalizedMap = {
      facebook: 'Facebook',
      instagram: 'Instagram',
      'google business profile': 'Google Business Profile',
    };

    return normalizedMap[trimmed.toLowerCase()] || trimmed;
  };

  const formatCreatedAt = (timestamp) => {
    if (!timestamp) return '';

    try {
      return new Date(timestamp).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch (error) {
      return '';
    }
  };

  // Form state for adding
  const [accountName, setAccountName] = useState('');
  const [platform, setPlatform] = useState('Facebook');

  // State for editing
  const [editingAccount, setEditingAccount] = useState(null);
  const [editName, setEditName] = useState('');
  const [editPlatform, setEditPlatform] = useState('');

  const fetchAccounts = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/api/social-media/social-accounts', {
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
    if (!accountName || !platform) return;
    try {
      await api.post('/api/social-media/social-accounts', {
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

  const handleDeleteAccount = async (accountId) => {
    if (window.confirm("Are you sure you want to delete this account?")) {
      try {
        await api.delete(`/api/social-media/social-accounts/${accountId}`);
        fetchAccounts();
      } catch (err) {
        alert('Failed to delete account.');
      }
    }
  };

  const handleStartEdit = (account) => {
    setEditingAccount(account);
    setEditName(account.account_name);
    const normalized = normalizePlatform(account.platform);
    setEditPlatform(normalized || account.platform || 'Facebook');
  };

  const handleCancelEdit = () => setEditingAccount(null);

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/api/social-media/social-accounts/${editingAccount.id}`, {
        account_name: editName,
        platform: editPlatform,
      });
      setEditingAccount(null);
      fetchAccounts();
    } catch (err) {
      alert('Failed to save changes.');
    }
  };

  const getPlatformClassName = (value) => {
    const normalized = normalizePlatform(value);
    const key = normalized.replace(/\s+/g, '').toLowerCase();
    return styles[key] ? `${styles.platform} ${styles[key]}` : styles.platform;
  };

  const renderAccounts = () => {
    if (isLoading) {
      return <p className={styles.emptyState}>Loading accounts...</p>;
    }

    if (error) {
      return <p className={styles.error}>{error}</p>;
    }

    if (accounts.length === 0) {
      return <p className={styles.emptyState}>No accounts yet. Connect your first profile above.</p>;
    }

    return (
      <ul className={styles.accountList}>
        {accounts.map((account) => {
          const { id, account_name, platform, is_active, created_at } = account;
          const normalizedPlatform = normalizePlatform(platform);
          const platformLabel =
            platformIconLabels[normalizedPlatform] || (normalizedPlatform ? normalizedPlatform.charAt(0).toUpperCase() : '?');
          const createdAtLabel = formatCreatedAt(created_at);
          const statusClass = `${styles.statusChip} ${is_active ? styles.statusActive : styles.statusInactive}`;

          return (
            <li key={id}>
              <div className={styles.accountInfo}>
                <div className={getPlatformClassName(platform)}>{platformLabel}</div>
                <div className={styles.accountDetails}>
                  <span className={styles.accountName}>{account_name}</span>
                  <span className={styles.accountPlatform}>{normalizedPlatform || 'Unknown Platform'}</span>
                </div>
              </div>
              <div className={styles.accountMeta}>
                <span className={statusClass}>{is_active ? 'Active' : 'Inactive'}</span>
                {createdAtLabel && <span className={styles.timestamp}>Added {createdAtLabel}</span>}
                <div className={styles.accountActions}>
                  <button type="button" onClick={() => handleStartEdit(account)} className={styles.editButton}>
                    Edit
                  </button>
                  <button type="button" onClick={() => handleDeleteAccount(id)} className={styles.deleteButton}>
                    Delete
                  </button>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    );
  };

  return (
    <div className={styles.container}>
      {editingAccount && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <h3>Edit Account</h3>
            <form onSubmit={handleSaveEdit}>
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                placeholder="Account name"
                required
              />
              <select value={editPlatform} onChange={(e) => setEditPlatform(e.target.value)}>
                <option>Facebook</option>
                <option>Instagram</option>
                <option>Google Business Profile</option>
              </select>
              <div className={styles.modalActions}>
                <button type="button" onClick={handleCancelEdit} className={styles.cancelButton}>
                  Cancel
                </button>
                <button type="submit" className={styles.saveButton}>
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <section className={styles.card}>
        <h3>Connect a New Account</h3>
        <form onSubmit={handleAddAccount} className={styles.form}>
          <input
            type="text"
            value={accountName}
            onChange={(e) => setAccountName(e.target.value)}
            placeholder="e.g., Main Facebook Page"
            required
          />
          <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
            <option>Facebook</option>
            <option>Instagram</option>
            <option>Google Business Profile</option>
          </select>
          <button type="submit">Add Account</button>
        </form>
      </section>

      <section className={styles.card}>
        <h3>Your Connected Accounts</h3>
        {renderAccounts()}
      </section>
    </div>
  );
}

export default AccountManager;
