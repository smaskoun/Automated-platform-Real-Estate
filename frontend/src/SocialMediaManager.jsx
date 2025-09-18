import React, { useState, useEffect, useRef } from 'react';
import api from './api.js';
import { useKeywordSets } from './KeywordSetsContext.jsx';
import styles from './SocialMediaManager.module.css';

// Simple debounce utility
function debounce(fn, delay) {
  let timeoutId;
  return (...args) => {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

function normalizeHashtag(value) {
  if (!value) return '';
  const cleaned = value
    .toString()
    .trim()
    .replace(/[#\s]+/g, ' ')
    .split(' ')
    .filter(Boolean)
    .join('');

  return cleaned ? `#${cleaned}` : '';
}

function SocialMediaManager({ user }) {
  const [posts, setPosts] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [brandVoices, setBrandVoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [insightWarning, setInsightWarning] = useState('');

  // Form state
  const [selectedAccount, setSelectedAccount] = useState('');
  const [content, setContent] = useState('');
  const [imagePrompt, setImagePrompt] = useState('');
  const [hashtags, setHashtags] = useState([]);
  const [scheduledAt, setScheduledAt] = useState('');

  // AI Generation state
  const [topic, setTopic] = useState('');
  const [selectedBrandVoice, setSelectedBrandVoice] = useState('');
  const [primaryKeyword, setPrimaryKeyword] = useState('');
  const [seoResult, setSeoResult] = useState(null);
  const [isKeywordPickerOpen, setIsKeywordPickerOpen] = useState(false);

  // Editing state
  const [editingPost, setEditingPost] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [editHashtags, setEditHashtags] = useState('');
  const [editSchedule, setEditSchedule] = useState('');

  const { savedKeywordSets } = useKeywordSets();

  const fetchData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const [accountsRes, postsRes, brandVoicesRes] = await Promise.all([
        api.get('/api/social-media/social-accounts', { params: { user_id: user.id } }),
        api.get('/api/social-media/posts', { params: { user_id: user.id } }),
        api.get('/api/brand-voices/', { params: { user_id: user.id } })
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
      const response = await api.post('/api/social-media/posts/generate', {
        user_id: user.id,
        topic: topic,
        brand_voice_id: selectedBrandVoice,
      });

      setContent(response.data.content || '');
      setHashtags(response.data.hashtags || []);
      setImagePrompt(response.data.image_prompt || '');
      if (response.data.insights_used === false) {
        setInsightWarning('Generated without performance insights due to insufficient data.');
      } else {
        setInsightWarning('');
      }

    } catch (err) {
      setError('AI content generation failed.');
      console.error("AI generation error:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  const analyzeKeyword = async (text) => {
    if (!primaryKeyword) {
      setSeoResult(null);
      return;
    }
    try {
      const res = await api.post('/api/seo-tools/keyword-density', {
        text,
        keyword: primaryKeyword,
      });
      setSeoResult(res.data);
    } catch (err) {
      console.error('Keyword density analysis failed:', err);
    }
  };

  const debouncedAnalyze = useRef(debounce(analyzeKeyword, 500));

  useEffect(() => {
    debouncedAnalyze.current = debounce(analyzeKeyword, 500);
  }, [primaryKeyword]);

  useEffect(() => {
    if (content && debouncedAnalyze.current) {
      debouncedAnalyze.current(content);
    }
  }, [content, primaryKeyword]);

  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!selectedAccount || !content) {
      alert("Please select an account and ensure there is content to post.");
      return;
    }
    try {
      await api.post('/api/social-media/posts', {
        account_id: selectedAccount,
        content: content,
        image_prompt: imagePrompt,
        hashtags: hashtags,
        scheduled_at: scheduledAt,
        user_id: user.id,
        status: 'draft'
      });

      alert("Post created successfully as a draft!");
      setContent('');
      setImagePrompt('');
      setTopic('');
      setHashtags([]);
      setScheduledAt('');
      fetchData();
    } catch (err) {
      console.error("Create post error:", err);
      alert("Failed to create the post.");
    }
  };
  const handleEditClick = (post) => {
    setEditingPost(post);
    setEditContent(post.content);
    setEditHashtags(post.hashtags ? post.hashtags.join(', ') : '');
    setEditSchedule(post.scheduled_at ? post.scheduled_at.slice(0, 16) : '');
  };

  const handleDelete = async (postId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;
    try {
      await api.delete(`/api/social-media/posts/${postId}`);
      setPosts(posts.filter(p => p.id !== postId));
    } catch (err) {
      console.error('Delete post error:', err);
      alert('Failed to delete the post.');
    }
  };

  const handleUpdatePost = async (e) => {
    e.preventDefault();
    if (!editingPost) return;
    try {
      await api.put(`/api/social-media/posts/${editingPost.id}`, {
        content: editContent,
        hashtags: editHashtags.split(',').map(t => t.trim()).filter(Boolean),
        scheduled_at: editSchedule ? new Date(editSchedule).toISOString() : null,
      });
      setEditingPost(null);
      fetchData();
    } catch (err) {
      console.error('Update post error:', err);
      alert('Failed to update the post.');
    }
  };

  const closeEditModal = () => {
    setEditingPost(null);
  };

  const applyKeywordSet = (keywordSet) => {
    if (!keywordSet) return;
    setPrimaryKeyword(keywordSet.primaryKeyword || keywordSet.keywords?.[0] || '');

    if (Array.isArray(keywordSet.hashtags) && keywordSet.hashtags.length > 0) {
      setHashtags(keywordSet.hashtags.map(normalizeHashtag).filter(Boolean));
    } else if (Array.isArray(keywordSet.keywords)) {
      const derived = keywordSet.keywords
        .filter((kw) => kw && kw !== keywordSet.primaryKeyword)
        .map(normalizeHashtag)
        .filter(Boolean);
      setHashtags(derived);
    } else {
      setHashtags([]);
    }

    setIsKeywordPickerOpen(false);
  };

  const getStatusClass = (status = '') => {
    const normalized = status.toLowerCase();
    if (normalized === 'draft') return styles.statusDraft;
    if (normalized === 'scheduled') return styles.statusScheduled;
    if (normalized === 'posted' || normalized === 'published' || normalized === 'approved') {
      return styles.statusPublished;
    }
    return styles.statusDefault;
  };

  if (isLoading) {
    return <div className={styles.loading}>Loading social media dashboard...</div>;
  }

  return (
    <div className={styles.manager}>
      {error && <div className={styles.error}>{error}</div>}
      {insightWarning && <div className={styles.warning}>{insightWarning}</div>}

      <div className={styles.layout}>
        <section className={styles.formCard}>
          <h3>Create New Social Media Post</h3>

          <div className={styles.aiSection}>
            <h4>✨ AI Content Generator</h4>
            <label className={styles.field}>
              Post Topic
              <input
                type="text"
                placeholder="Enter post topic..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </label>
            <div className={styles.inlineRow}>
              <input
                type="text"
                placeholder="Primary keyword..."
                value={primaryKeyword}
                onChange={(e) => setPrimaryKeyword(e.target.value)}
              />
              <button type="button" onClick={() => setIsKeywordPickerOpen(true)} className={styles.secondaryButton}>
                Import Saved
              </button>
            </div>
            <label className={styles.field}>
              Brand Voice
              <select value={selectedBrandVoice} onChange={(e) => setSelectedBrandVoice(e.target.value)}>
                <option value="" disabled>
                  Select a Brand Voice
                </option>
                {brandVoices.map((bv) => (
                  <option key={bv.id} value={bv.id}>
                    {bv.name}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              onClick={handleGenerateContent}
              disabled={isGenerating}
              className={styles.primaryButton}
            >
              {isGenerating ? 'Generating...' : 'Generate with AI'}
            </button>
          </div>

          <form onSubmit={handleCreatePost} className={styles.postForm}>
            <label className={styles.field}>
              Select Account
              <select value={selectedAccount} onChange={(e) => setSelectedAccount(e.target.value)} required>
                <option value="" disabled>
                  Select an account to post to
                </option>
                {accounts.map((acc) => (
                  <option key={acc.id} value={acc.id}>
                    {acc.account_name} ({acc.platform})
                  </option>
                ))}
              </select>
            </label>
            <label className={`${styles.field} ${styles.fullWidth}`}>
              Post Copy
              <textarea
                placeholder="AI-generated content will appear here..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                required
                rows={8}
              />
            </label>
            {seoResult && (
              <div className={styles.seoResult}>
                <p>
                  <strong>Keyword Density:</strong> {seoResult.keyword_density}%
                </p>
                <p>
                  <strong>Keyword Count:</strong> {seoResult.keyword_count}
                </p>
                <p>
                  <strong>Total Words:</strong> {seoResult.total_words}
                </p>
                <p>{seoResult.suggestion}</p>
              </div>
            )}
            <label className={styles.field}>
              Image Prompt
              <input
                type="text"
                placeholder="AI-generated image prompt will appear here..."
                value={imagePrompt}
                onChange={(e) => setImagePrompt(e.target.value)}
              />
            </label>
            <div className={styles.hashtagGroup}>
              <span className={styles.fieldLabel}>Generated Hashtags</span>
              <div className={styles.hashtagContainer}>
                {hashtags.length > 0 ? (
                  hashtags.map((tag, index) => (
                    <span key={index} className={styles.hashtagItem}>
                      {tag}
                    </span>
                  ))
                ) : (
                  <span className={styles.noHashtags}>Hashtags will appear here...</span>
                )}
              </div>
            </div>
            <label className={styles.field}>
              Schedule
              <input
                type="datetime-local"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
              />
            </label>
            <div className={styles.formActions}>
              <button type="submit" className={styles.primaryButton}>
                Create &amp; Schedule Post
              </button>
            </div>
          </form>
        </section>

        <section className={styles.listCard}>
          <div className={styles.listHeader}>
            <h3>Scheduled &amp; Draft Posts</h3>
            <span className={styles.postCount}>{posts.length} total</span>
          </div>
          {posts.length > 0 ? (
            <ul className={styles.postList}>
              {posts.map((post) => {
                const statusChip = `${styles.statusChip} ${getStatusClass(post.status)}`;
                return (
                  <li key={post.id} className={styles.postItem}>
                    <div className={styles.postContent}>
                      <p>{post.content}</p>
                      {post.hashtags && post.hashtags.length > 0 && (
                        <div className={styles.postHashtags}>
                          {post.hashtags.map((tag, index) => (
                            <span key={index} className={styles.hashtagItem}>
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                      {post.image_prompt && (
                        <p className={styles.postMeta}>
                          <span>Image Prompt:</span> {post.image_prompt}
                        </p>
                      )}
                      {post.scheduled_at && (
                        <p className={styles.postMeta}>
                          <span>Scheduled for:</span> {new Date(post.scheduled_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                    <div className={styles.postSidebar}>
                      <span className={statusChip}>{post.status}</span>
                      <span className={styles.accountLabel}>{post.account_name}</span>
                      <div className={styles.postActions}>
                        <button type="button" onClick={() => handleEditClick(post)} className={styles.secondaryButton}>
                          Edit
                        </button>
                        <button type="button" onClick={() => handleDelete(post.id)} className={styles.deleteButton}>
                          Delete
                        </button>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className={styles.emptyState}>No posts found. Use the form to craft your first campaign.</p>
          )}
        </section>
      </div>

      {editingPost && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <h3 className={styles.modalTitle}>Edit Post</h3>
            <form onSubmit={handleUpdatePost}>
              <label className={styles.field}>
                Post Content
                <textarea value={editContent} onChange={(e) => setEditContent(e.target.value)} rows={6} />
              </label>
              <label className={styles.field}>
                Hashtags (comma separated)
                <input
                  type="text"
                  value={editHashtags}
                  onChange={(e) => setEditHashtags(e.target.value)}
                  placeholder="#realestate, #windsorhomes"
                />
              </label>
              <label className={styles.field}>
                Schedule
                <input
                  type="datetime-local"
                  value={editSchedule}
                  onChange={(e) => setEditSchedule(e.target.value)}
                />
              </label>
              <div className={styles.modalActions}>
                <button type="button" onClick={closeEditModal} className={styles.secondaryButton}>
                  Cancel
                </button>
                <button type="submit" className={styles.primaryButton}>
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isKeywordPickerOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.keywordModal}>
            <div className={styles.keywordHeader}>
              <div>
                <h3>Import Saved Keywords</h3>
                <p>Select a keyword set saved from the SEO Tools page.</p>
              </div>
              <button type="button" onClick={() => setIsKeywordPickerOpen(false)} className={styles.closeButton}>
                Close
              </button>
            </div>
            {savedKeywordSets.length === 0 ? (
              <p className={styles.emptyState}>No keyword sets available yet. Save some from the SEO Tools page.</p>
            ) : (
              <ul className={styles.keywordSetList}>
                {savedKeywordSets.map((set) => (
                  <li key={set.id} className={styles.keywordSetCard}>
                    <div className={styles.keywordSetMeta}>
                      <p className={styles.keywordSetName}>{set.name}</p>
                      {set.primaryKeyword && (
                        <p className={styles.keywordSetDetail}>Primary keyword: {set.primaryKeyword}</p>
                      )}
                      {set.keywords?.length > 0 && (
                        <p className={styles.keywordSetDetail}>Keywords: {set.keywords.join(', ')}</p>
                      )}
                      {set.hashtags?.length > 0 && (
                        <div className={styles.savedHashtagContainer}>
                          {set.hashtags.map((tag, idx) => (
                            <span key={idx} className={styles.savedHashtagItem}>
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className={styles.keywordSetActions}>
                      <button type="button" onClick={() => applyKeywordSet(set)} className={styles.primaryButton}>
                        Use
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default SocialMediaManager;
