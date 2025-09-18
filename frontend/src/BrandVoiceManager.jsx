import React, { useState, useEffect } from 'react';
import api from './api.js';
import styles from './BrandVoiceManager.module.css';

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

  const formatDate = (value) => {
    if (!value) return '';
    try {
      return new Date(value).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch (err) {
      console.error('Failed to parse date', err);
      return '';
    }
  };

  if (isLoading) {
    return <div className={styles.loading}>Loading source content...</div>;
  }

  if (error) {
    return <div className={styles.errorBanner}>{error}</div>;
  }

  return (
    <div className={styles.container}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h3 className={styles.cardTitle}>Add New Source Content</h3>
            <p className={styles.cardSubtitle}>
              Curate your top-performing posts to train the AI brand voice engine.
            </p>
          </div>
        </div>
        <form onSubmit={handleCreateVoice} className={styles.formGrid}>
          <label htmlFor="voiceName" className={styles.label}>
            Content Title
            <input
              id="voiceName"
              type="text"
              value={newVoiceName}
              onChange={(e) => setNewVoiceName(e.target.value)}
              placeholder="e.g., Luxury waterfront open house"
              className={styles.input}
              required
            />
          </label>
          <label htmlFor="voiceDesc" className={styles.label}>
            Short Description
            <input
              id="voiceDesc"
              type="text"
              value={newVoiceDesc}
              onChange={(e) => setNewVoiceDesc(e.target.value)}
              placeholder="What makes this content special?"
              className={styles.input}
              required
            />
          </label>
          <label htmlFor="postExample" className={`${styles.label} ${styles.fullWidth}`}>
            Full Post Content
            <textarea
              id="postExample"
              value={newPostExample}
              onChange={(e) => setNewPostExample(e.target.value)}
              placeholder="Paste the full copy of the post you loved..."
              className={styles.textarea}
              required
              rows="8"
            />
            <span className={styles.helperText}>Include emojis, formatting, and hashtags for the best training results.</span>
          </label>
          <div className={`${styles.cardActions} ${styles.fullWidth}`}>
            <button type="submit" className={styles.primaryButton}>
              Add Content
            </button>
          </div>
        </form>
      </section>

      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h3 className={styles.cardTitle}>Upload Previous Posts in Bulk</h3>
            <p className={styles.cardSubtitle}>
              Paste multiple winning posts to fast-track your training dataset.
            </p>
          </div>
        </div>
        <form onSubmit={handleUploadExamples} className={styles.formGrid}>
          <label htmlFor="voiceSelect" className={styles.label}>
            Select Source Content
            <select
              id="voiceSelect"
              value={selectedVoiceId}
              onChange={(e) => setSelectedVoiceId(e.target.value)}
              className={styles.select}
              required
            >
              <option value="" disabled>
                Choose a saved voice
              </option>
              {voices.map((voice) => (
                <option key={voice.id} value={voice.id}>
                  {voice.name}
                </option>
              ))}
            </select>
          </label>
          <label htmlFor="bulkExamples" className={`${styles.label} ${styles.fullWidth}`}>
            Posts (separate with blank lines)
            <textarea
              id="bulkExamples"
              value={bulkExamples}
              onChange={(e) => setBulkExamples(e.target.value)}
              placeholder="Paste each post on its own with a blank line between"
              className={styles.textarea}
              rows="6"
              required
            />
            <span className={styles.helperText}>
              We’ll split on blank lines so you can paste entire batches from your archives.
            </span>
          </label>
          <div className={`${styles.cardActions} ${styles.fullWidth}`}>
            <button type="submit" className={styles.secondaryButton}>
              Upload Posts
            </button>
          </div>
        </form>
      </section>

      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h3 className={styles.cardTitle}>Source Content Library</h3>
            <p className={styles.cardSubtitle}>
              Review and manage the reference posts that power your automations.
            </p>
          </div>
        </div>
        {voices.length > 0 ? (
          <ul className={styles.libraryList}>
            {voices.map((voice) => (
              <li key={voice.id} className={styles.libraryItem}>
                <div className={styles.voiceHeader}>
                  <h4 className={styles.voiceName}>{voice.name}</h4>
                  <span className={`${styles.statusChip} ${styles.statusReady}`}>Ready</span>
                </div>
                <p className={styles.voiceDescription}>{voice.description}</p>
                <div className={styles.postExample}>
                  <span className={styles.postLabel}>Example Post</span>
                  <p className={styles.postBody}>{voice.post_example}</p>
                </div>
                <div className={styles.libraryMeta}>
                  <span className={styles.timestamp}>
                    {voice.created_at ? `Added ${formatDate(voice.created_at)}` : 'Creation date unavailable'}
                  </span>
                  <div className={styles.libraryActions}>
                    <button type="button" onClick={() => handleDeleteVoice(voice.id)} className={styles.dangerButton}>
                      Delete
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.emptyState}>
            You haven&apos;t added any source content yet. Capture a post above to get started.
          </p>
        )}
      </section>
    </div>
  );
}

export default BrandVoiceManager;
