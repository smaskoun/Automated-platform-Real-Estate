import React, { useState, useEffect } from 'react';
import api from './api.js';

function BrandVoiceManager({ user }) {
  const [voices, setVoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [newVoiceName, setNewVoiceName] = useState('');
  const [newVoiceDesc, setNewVoiceDesc] = useState('');
  const [newPostExample, setNewPostExample] = useState('');

  // State for bulk example upload
  const [selectedVoiceId, setSelectedVoiceId] = useState('');
  const [bulkExamples, setBulkExamples] = useState('');

  const fetchVoices = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await api.get('/api/brand-voices/', {
        params: { user_id: user.id }
      });
      setVoices(response.data.brand_voices || []);
    } catch (err) {
      setError('Failed to fetch brand voices.');
      console.error('Fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (user && user.id) {
      fetchVoices();
    }
  }, [user]);

  const handleCreateVoice = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/brand-voices/', {
        user_id: user.id,
        name: newVoiceName,
        description: newVoiceDesc,
        post_example: newPostExample,
      });
      setNewVoiceName('');
      setNewVoiceDesc('');
      setNewPostExample('');
      fetchVoices();
    } catch (err) {
      console.error('Create error:', err);
      alert('Failed to create source content.');
    }
  };

  const handleDeleteVoice = async (voiceId) => {
    if (window.confirm('Are you sure you want to delete this source content?')) {
      try {
        await api.delete(`/api/brand-voices/${voiceId}/`);
        fetchVoices();
      } catch (err) {
        console.error('Delete error:', err);
        alert('Failed to delete source content.');
      }
    }
  };

  const handleUploadExamples = async (e) => {
    e.preventDefault();
    if (!selectedVoiceId) return;
    const examples = bulkExamples
      .split(/\r?\n\s*\r?\n/)
      .map((p) => p.replace(/\r/g, '').trim())
      .filter((p) => p);
    if (examples.length === 0) return;
    try {
      await api.post(`/api/brand-voices/${selectedVoiceId}/examples/batch`, {
        examples,
      });
      setBulkExamples('');
      setSelectedVoiceId('');
      fetchVoices();
    } catch (err) {
      console.error('Bulk upload error:', err);
      alert('Failed to upload examples.');
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <div className="text-lg font-medium text-gray-500">Loading Source Content...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-red-700">
        {error}
      </div>
    );
  }

  const inputClasses =
    'w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500';

  return (
    <div className="space-y-8">
      <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
        <h3 className="mb-6 text-xl font-semibold text-gray-900">Add New Source Content</h3>
        <form onSubmit={handleCreateVoice} className="space-y-6">
          <div className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="voiceName" className="block text-sm font-medium text-gray-700">
                Content Title
              </label>
              <input
                id="voiceName"
                type="text"
                placeholder="e.g., 'Just Listed - 123 Main St'"
                value={newVoiceName}
                onChange={(e) => setNewVoiceName(e.target.value)}
                className={inputClasses}
                required
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="voiceDesc" className="block text-sm font-medium text-gray-700">
                Short Description
              </label>
              <input
                id="voiceDesc"
                type="text"
                placeholder="e.g., 'Successful post from May 2024'"
                value={newVoiceDesc}
                onChange={(e) => setNewVoiceDesc(e.target.value)}
                className={inputClasses}
                required
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="postExample" className="block text-sm font-medium text-gray-700">
                Full Post Content
              </label>
              <textarea
                id="postExample"
                placeholder="Paste the full content of your successful post here..."
                value={newPostExample}
                onChange={(e) => setNewPostExample(e.target.value)}
                className={`${inputClasses} min-h-[200px] resize-y`}
                required
                rows="8"
              />
            </div>
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-lg bg-primary-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            >
              Add Content
            </button>
          </div>
        </form>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
        <h3 className="mb-6 text-xl font-semibold text-gray-900">Upload Previous Posts in Bulk</h3>
        <form onSubmit={handleUploadExamples} className="space-y-6">
          <div className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="voiceSelect" className="block text-sm font-medium text-gray-700">
                Select Voice
              </label>
              <select
                id="voiceSelect"
                value={selectedVoiceId}
                onChange={(e) => setSelectedVoiceId(e.target.value)}
                className={`${inputClasses} bg-white`}
                required
              >
                <option value="" disabled>
                  Select a voice
                </option>
                {voices.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label htmlFor="bulkExamples" className="block text-sm font-medium text-gray-700">
                Posts (separate with blank lines)
              </label>
              <textarea
                id="bulkExamples"
                rows="6"
                placeholder="Paste multiple posts here..."
                value={bulkExamples}
                onChange={(e) => setBulkExamples(e.target.value)}
                className={`${inputClasses} min-h-[160px] resize-y`}
                required
              />
            </div>
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-lg bg-primary-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            >
              Upload Posts
            </button>
          </div>
        </form>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
        <h3 className="mb-6 text-xl font-semibold text-gray-900">Your Source Content Library</h3>
        {voices.length > 0 ? (
          <ul className="space-y-6">
            {voices.map((voice) => (
              <li
                key={voice.id}
                className="flex flex-col gap-4 rounded-lg border border-gray-200 p-6 md:flex-row md:items-start md:justify-between"
              >
                <div className="flex-1">
                  <strong className="block text-lg font-semibold text-gray-900">{voice.name}</strong>
                  <p className="mt-2 text-gray-600">{voice.description}</p>
                  <pre className="mt-4 whitespace-pre-wrap break-words rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm leading-relaxed text-gray-800">
                    {voice.post_example}
                  </pre>
                </div>
                <div className="flex items-start md:flex-col md:items-end">
                  <button
                    onClick={() => handleDeleteVoice(voice.id)}
                    className="inline-flex items-center justify-center rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-600">
            You haven't added any source content yet. Use the form above to get started.
          </p>
        )}
      </div>
    </div>
  );
}

export default BrandVoiceManager;
