// frontend/src/SocialMediaManager.jsx - FULL REPLACEMENT

import React, { useState, useEffect } from 'react';
import styles from './SocialMediaManager.module.css';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function SocialMediaManager({ user }) {
  const [posts, setPosts] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [brandVoices, setBrandVoices] = useState([]); // State for Brand Voices
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false); // State for AI generation
  const [error, setError] = useState('');

  // Form state
  const [selectedAccount, setSelectedAccount] = useState('');
  const [content, setContent] = useState('');
  const [imagePrompt, setImagePrompt] = useState('');
  const [hashtags, setHashtags] = useState([]); // State for hashtags

  // AI Generation state
  const [topic, setTopic] = useState('');
  const [selectedBrandVoice, setSelectedBrandVoice] = useState('');

  // Function to fetch all necessary data
  const fetchData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const [accountsRes, postsRes, brandVoicesRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/social-media/social-accounts`, { params: { user_id: user.id } }),
        axios.get(`${API_BASE_URL}/social-media/posts`, { params: { user_id: user.id } }),
        axios.get(`${API_BASE_URL}/brand-voices/`, { params: { user_id: user.id } }) // Fetch Brand Voices
      ]);
      
      setAccounts(accountsRes.data.accounts || []);
      setPosts(postsRes.data.posts || []);
      setBrandVoices(brandVoicesRes.data.brand_voices || []);

      if (accountsRes.data.accounts?.length > 0) {
        setSelectedAccount(accountsRes.data.accounts[0].id);
      }
      if (brandVoicesRes.data.brand_voices?.length > 0) {
        setSelectedBrandVoice(brandVoicesRes.data.brand_voices[0].id);
      }

    } catch (err) {
      setError('Failed to fetch initial data. Please refresh the page.');
      console.error("Fetch error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (user?.id) {
      fetchData();
    }
  }, [user]);

  // --- NEW: Handle AI Content Generation ---
  const handleGenerateContent = async () => {
    if (!topic || !selectedBrandVoice) {
      alert("Please provide a topic and select a brand voice.");
      return;
    }
    setIsGenerating(true);
    setError('');
    try {
      const response = await axios.post(`${API_BASE_URL}/social-media/posts/generate`, {
        user_id: user.id,
        topic: topic,
        brand_voice_id: selectedBrandVoice,
      });
      
      // Populate content and hashtags with AI response
      setContent(response.data.content || '');
      setHashtags(response.data.hashtags || []);

    } catch (err) {
      setError('AI content generation failed.');
      console.error("AI generation error:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  // Handle form submission for a new post
  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!selectedAccount) {
      alert("Please select a social media account.");
      return;
    }
    try {
      await axios.post(`${API_BASE_URL}/social-media/posts`, {
        account_id: selectedAccount,
        content: content,
        image_prompt: imagePrompt,
        hashtags: hashtags, // Use the hashtags from state
      });
      // Reset form and refresh data
      setContent('');
      setImagePrompt('');
      setTopic('');
      setHashtags([]);
      fetchData();
    } catch (err) {
      console.error("Create post error:", err);
      alert("Failed to create post.");
    }
  };

  if (isLoading) {
    return <div className={styles.loading}>Loading social media dashboard...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  return (
    <div className={styles.manager}>
      <div className={styles.formCard}>
        <h3>Create New Social Media Post</h3>
        
        {/* --- AI Generation Section --- */}
        <div className={styles.aiSection}>
          <h4>✨ AI Content Generator</h4>
          <input
            type="text"
            placeholder="Enter post topic (e.g., 'New 2-bed condo downtown')"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
          <select value={selectedBrandVoice} onChange={(e) => setSelectedBrandVoice(e.target.value)}>
            <option value="" disabled>Select a Brand Voice</option>
            {brandVoices.map(bv => (
              <option key={bv.id} value={bv.id}>{bv.name}</option>
            ))}
          </select>
          <button type="button" onClick={handleGenerateContent} disabled={isGenerating}>
            {isGenerating ? 'Generating...' : 'Generate with AI'}
          </button>
        </div>

        {/* --- Post Creation Form --- */}
        <form onSubmit={handleCreatePost}>
          <select value={selectedAccount} onChange={(e) => setSelectedAccount(e.target.value)} required>
            <option value="" disabled>Select an Account to Post To</option>
            {accounts.map(acc => (
              <option key={acc.id} value={acc.id}>{acc.account_name} ({acc.platform})</option>
            ))}
          </select>
          <textarea
            placeholder="AI-generated content will appear here..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            rows={8}
          />
          <input
            type="text"
            placeholder="Describe the image you want (e.g., 'modern kitchen')"
            value={imagePrompt}
            onChange={(e) => setImagePrompt(e.g.target.value)}
          />
          <div className={styles.hashtags}>
            {hashtags.map((tag, index) => <span key={index} className={styles.tag}>{tag}</span>)}
          </div>
          <button type="submit">Create & Schedule Post</button>
        </form>
      </div>

      <div className={styles.listCard}>
        <h3>Scheduled & Draft Posts</h3>
        {posts.length > 0 ? (
          <ul className={styles.postList}>
            {posts.map((post) => (
              <li key={post.id} className={`${styles.postItem} ${styles[post.status]}`}>
                <div className={styles.postContent}>
                  <p>{post.content}</p>
                  <small>Status: {post.status}</small>
                </div>
                <div className={styles.postActions}>
                  <button>Approve</button>
                  <button className={styles.deleteButton}>Delete</button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>No posts found. Use the form to create one.</p>
        )}
      </div>
    </div>
  );
}

export default SocialMediaManager;
