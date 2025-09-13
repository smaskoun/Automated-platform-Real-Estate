import React, { useEffect, useState } from 'react';
import api from './api.js';

function AbTesting() {
  const [testName, setTestName] = useState('');
  const [tests, setTests] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const fetchTests = async () => {
    try {
      const res = await api.get('/api/ab-testing/tests');
      setTests(res.data.tests || []);
    } catch (err) {
      console.error('Failed to load tests:', err);
      setError('Failed to load existing tests.');
    }
  };

  useEffect(() => {
    fetchTests();
  }, []);

  const handleCreateTest = async () => {
    if (!testName.trim()) {
      setError('Test name is required.');
      return;
    }
    try {
      const res = await api.post('/api/ab-testing/create-test', { test_name: testName });
      setMessage(res.data.message || 'Test created successfully');
      setTestName('');
      setError('');
      fetchTests();
    } catch (err) {
      console.error('Failed to create test:', err);
      setError('Failed to create test.');
      setMessage('');
    }
  };

  return (
    <div className="space-y-8">
      <div className="max-w-lg bg-white p-6 rounded-lg shadow-md space-y-4">
        <h2 className="text-2xl font-bold">Create A/B Test</h2>
        <input
          type="text"
          value={testName}
          onChange={(e) => setTestName(e.target.value)}
          placeholder="Enter test name"
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
        <button
          type="button"
          onClick={handleCreateTest}
          className="px-4 py-2 font-semibold text-white bg-purple-600 rounded-md hover:bg-purple-700"
        >
          Create Test
        </button>
        {message && <div className="text-green-600">{message}</div>}
        {error && <div className="text-red-600">{error}</div>}
      </div>

      <div className="max-w-2xl">
        <h3 className="text-xl font-semibold mb-4">Existing Tests</h3>
        {tests.length > 0 ? (
          <ul className="space-y-2">
            {tests.map((t) => (
              <li key={t.id} className="p-4 bg-white rounded-md shadow">
                <p className="font-medium">{t.name}</p>
                <p className="text-sm text-gray-500">Status: {t.status}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No tests found.</p>
        )}
      </div>
    </div>
  );
}

export default AbTesting;

