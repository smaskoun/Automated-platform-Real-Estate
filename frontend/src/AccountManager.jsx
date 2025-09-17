import React, { useState, useEffect } from 'react';
import api from './api.js';

// A simple, reusable button component for consistent styling
const Button = ({ onClick, children, className, type = "button" }) => (
  <button
    type={type}
    onClick={onClick}
    className={`px-4 py-2 font-semibold text-white rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 ${className}`}
  >
    {children}
  </button>
);

function AccountManager({ user }) {
  const [accounts, setAccounts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const platformIconStyles = {
    Facebook: 'bg-blue-100 text-blue-600',
    Instagram: 'bg-pink-100 text-pink-600',
    'Google Business Profile': 'bg-yellow-100 text-yellow-600',
  };

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

  return (
    <div className="space-y-8">
      {/* Edit Modal */}
      {editingAccount && (
        <div className="fixed inset-0 z-10 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-xl font-bold mb-4">Edit Account</h3>
            <form onSubmit={handleSaveEdit} className="space-y-4">
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
              <select value={editPlatform} onChange={(e) => setEditPlatform(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md">
                <option>Facebook</option>
                <option>Instagram</option>
                <option>Google Business Profile</option>
              </select>
              <div className="flex justify-end space-x-3">
                <Button onClick={handleCancelEdit} className="bg-gray-500 hover:bg-gray-600">Cancel</Button>
                <Button type="submit" className="bg-blue-600 hover:bg-blue-700">Save Changes</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Account Card */}
      <div className="bg-white rounded-xl shadow-sm p-8 mb-8 border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Add New Account</h3>
        <form onSubmit={handleAddAccount} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            value={accountName}
            onChange={(e) => setAccountName(e.target.value)}
            placeholder="e.g., My Main Facebook Page"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-medium md:col-span-1"
            required
          />
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-medium"
          >
            <option>Facebook</option>
            <option>Instagram</option>
            <option>Google Business Profile</option>
          </select>
          <Button
            type="submit"
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors w-full md:w-auto"
          >
            Add Account
          </Button>
        </form>
      </div>

      {/* Your Accounts Card */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-bold mb-4">Your Accounts</h3>
        {isLoading ? <p>Loading accounts...</p> : error ? <p className="text-red-500">{error}</p> : (
          <ul className="space-y-4 mb-6">
            {accounts.length > 0 ? accounts.map((account) => {
              const { id, account_name, platform, is_active, created_at } = account;
              const normalizedPlatform = normalizePlatform(platform);
              const createdAtLabel = formatCreatedAt(created_at);
              const platformIconClass = platformIconStyles[normalizedPlatform] || 'bg-gray-100 text-gray-600';
              const platformIconLabel = platformIconLabels[normalizedPlatform] || (normalizedPlatform ? normalizedPlatform.charAt(0).toUpperCase() : '?');
              const statusClasses = is_active
                ? 'px-3 py-1 bg-success-50 text-success-700 rounded-full text-xs font-medium'
                : 'px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium';

              return (
                <li
                  key={id}
                  className="bg-white rounded-xl shadow-card hover:shadow-card-hover transition-all duration-200 p-6 border border-gray-200 mb-4 flex items-center justify-between gap-6 flex-col sm:flex-row"
                >
                  <div className="flex items-center w-full gap-4 sm:w-auto">
                    <div
                      className={`flex h-12 w-12 items-center justify-center rounded-xl text-sm font-semibold ${platformIconClass}`}
                    >
                      {platformIconLabel}
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-gray-500">{normalizedPlatform || 'Unknown Platform'}</p>
                      <h4 className="text-lg font-semibold text-gray-900">{account_name}</h4>
                      {createdAtLabel && (
                        <p className="text-sm text-gray-500">Added {createdAtLabel}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex w-full items-center justify-between gap-4 sm:w-auto sm:justify-end">
                    <span className={statusClasses}>{is_active ? 'Active' : 'Inactive'}</span>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => handleStartEdit(account)}
                        className="px-4 py-2 text-sm font-semibold rounded-lg bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300 transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteAccount(id)}
                        className="px-4 py-2 text-sm font-semibold rounded-lg bg-red-600 text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </li>
              );
            }) : <p>No accounts found. Add one using the form above.</p>}
          </ul>
        )}
      </div>
    </div>
  );
}

export default AccountManager;
