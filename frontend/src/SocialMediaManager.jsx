// frontend/src/SocialMediaManager.jsx - FULL REPLACEMENT (With AI Image Prompt)

import React, { useState, useEffect } from 'react';
import styles from './SocialMediaManager.module.css';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function SocialMediaManager({ user }) {
  const [posts, setPosts] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [brandVoices, setBrandVoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');

  // Form state
  const [selectedAccount, setSelectedAccount] = useState('');
  const [content, setContent] = useState('');
  const [imagePrompt, setImagePrompt] = useState(''); // This will now be set by the AI
  const [hashtags, setHashtags] = useState([]);

  // AI Generation state
  const [topic, setTopic] = useState('');
  const [selectedBrandVoice, setSelectedBrandVoice] = useState('');

  const fetchData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const [accountsRes, postsRes, brandVoicesRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/social-media/social-accounts`, { params: { user_id: user.id } }),
        axios.get(`${API_BASE_URL}/social-media/posts`, { params: { user_id: user.id } }),
        axios.get(`${API_BASE_URL}/brand-voices/`, { params: { user_id: user.id } })
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
      
      // --- THIS IS THE MODIFIED PART ---
      // Populate all three fields from the AI response
      setContent(response.data.content || '');
      setHashtags(response.data.hashtags || []);
      setImagePrompt(response.data.image_prompt || ''); // Set the image prompt

    } catch (err) {
      setError('AI content generation failed.');
      console.error("AI generation error:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!selectedAccount || !content) {
      alert("Please select an account and ensure there is content to post.");
      return;
    }
    try {
      await axios.post(`${API_BASE_URL}/social-media/posts`, {
        account_id: selectedAccount,
        content: content,
        image_prompt: imagePrompt,
        hashtags: hashtags,
        user_id: user.id,
        status: 'draft'
      });
      
      alert("Post created successfully as a draft!");
      setContent('');
      setImagePrompt('');
      setTopic('');
      setHashtags([]);
      fetchData();
    } catch (err) {
      console.error("Create post error:", err);
      alert("Failed to create the post.");
    }
  };

  if (isLoading) {
    return <div className={styles.loading}>Loading social media dashboard...</div>;
  }

  return (
    <div className={styles.manager}>
      <div className={styles.formCard}>
        <h3>Create New Social Media Post</h3>
        
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
        
        {error && <div className={styles.error}>{error}</div>}

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
          {/* This input is now controlled by the AI */}
          <input
            type="text"
            placeholder="AI-generated image prompt will appear here..."
            value={imagePrompt}
            onChange={(e) => setImagePrompt(e.target.value)}
          />
          
          <div className={styles.hashtagContainer}>
            {hashtags.length > 0 ? (
              hashtags.map((tag, index) => (
                <span key={index} className={styles.hashtagItem}>{tag}</span>
              ))
            ) : (
              <p className={styles.noHashtags}>Hashtags will appear here...</p>
            )}
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
                  <small>Status: {post.status} | Account: {post.account_name}</small>
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
