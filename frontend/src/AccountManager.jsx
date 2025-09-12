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
    setEditPlatform(account.platform);
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

  // Helper for platform-specific styling
  const platformStyles = {
    Facebook: 'bg-blue-500 text-white',
    Instagram: 'bg-pink-500 text-white',
    'Google Business Profile': 'bg-yellow-500 text-white',
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
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-bold mb-4">Add New Account</h3>
        <form onSubmit={handleAddAccount} className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <input
            type="text"
            value={accountName}
            onChange={(e) => setAccountName(e.target.value)}
            placeholder="e.g., My Main Facebook Page"
            className="w-full px-3 py-2 border border-gray-300 rounded-md md:col-span-1"
            required
          />
          <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option>Facebook</option>
            <option>Instagram</option>
            <option>Google Business Profile</option>
          </select>
          <Button type="submit" className="bg-blue-600 hover:bg-blue-700 w-full md:w-auto">Add Account</Button>
        </form>
      </div>

      {/* Your Accounts Card */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-bold mb-4">Your Accounts</h3>
        {isLoading ? <p>Loading accounts...</p> : error ? <p className="text-red-500">{error}</p> : (
          <ul className="space-y-3">
            {accounts.length > 0 ? accounts.map(acc => (
              <li key={acc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md border">
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 text-xs font-bold rounded-full ${platformStyles[acc.platform]}`}>{acc.platform}</span>
                  <span className="font-medium">{acc.account_name}</span>
                </div>
                <div className="flex space-x-2">
                  <Button onClick={() => handleStartEdit(acc)} className="bg-yellow-500 hover:bg-yellow-600 text-sm">Edit</Button>
                  <Button onClick={() => handleDeleteAccount(acc.id)} className="bg-red-600 hover:bg-red-700 text-sm">Delete</Button>
                </div>
              </li>
            )) : <p>No accounts found. Add one using the form above.</p>}
          </ul>
        )}
      </div>
    </div>
  );
}

export default AccountManager;
