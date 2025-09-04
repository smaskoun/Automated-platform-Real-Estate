
// frontend/src/SocialMediaManager.jsx

import React, { useState, useEffect } from 'react';
import styles from './SocialMediaManager.module.css'; // We will create this file next
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function SocialMediaManager({ user }) {
  const [posts, setPosts] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Form state
  const [selectedAccount, setSelectedAccount] = useState('');
  const [content, setContent] = useState('');
  const [imagePrompt, setImagePrompt] = useState('');

  // Function to fetch all necessary data
  const fetchData = async () => {
    setIsLoading(true);
    setError('');
    try {
      // Fetch both accounts and posts at the same time
      const [accountsResponse, postsResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/social-media/social-accounts`, { params: { user_id: user.id } }),
        axios.get(`${API_BASE_URL}/social-media/posts`, { params: { user_id: user.id } })
      ]);
      
      setAccounts(accountsResponse.data.accounts || []);
      setPosts(postsResponse.data.posts || []);

      // Set a default selected account if one exists
      if (accountsResponse.data.accounts && accountsResponse.data.accounts.length > 0) {
        setSelectedAccount(accountsResponse.data.accounts[0].id);
      }

    } catch (err) {
      setError('Failed to fetch social media data. Please try again later.');
      console.error("Fetch error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch data when the component loads
  useEffect(() => {
    if (user && user.id) {
      fetchData();
    }
  }, [user]);

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
        hashtags: ["#realestate", "#newlisting"], // Placeholder hashtags
      });
      // Reset form and refresh data
      setContent('');
      setImagePrompt('');
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
        <form onSubmit={handleCreatePost}>
          <select value={selectedAccount} onChange={(e) => setSelectedAccount(e.target.value)} required>
            <option value="" disabled>Select an Account</option>
            {accounts.map(acc => (
              <option key={acc.id} value={acc.id}>{acc.account_name} ({acc.platform})</option>
            ))}
          </select>
          <textarea
            placeholder="Write your post content here..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Describe the image you want to generate (e.g., 'a modern kitchen with marble countertops')"
            value={imagePrompt}
            onChange={(e) => setImagePrompt(e.target.value)}
          />
          <button type="submit">Create Post</button>
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
          <p>No posts found. Use the form above to create one.</p>
        )}
      </div>
    </div>
  );
}

export default SocialMediaManager;
