import React, { useState, useEffect } from 'react';
import api from './api.js';

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
  const [imagePrompt, setImagePrompt] = useState('');
  const [hashtags, setHashtags] = useState([]);

  // AI Generation state
  const [topic, setTopic] = useState('');
  const [selectedBrandVoice, setSelectedBrandVoice] = useState('');

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
      await api.post('/api/social-media/posts', {
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
    return <div className="text-center p-8">Loading social media dashboard...</div>;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Left Column: Form Card */}
      <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow-md space-y-6">
        <h3 className="text-xl font-bold">Create New Social Media Post</h3>
        
        {/* AI Generator Section */}
        <div className="p-4 bg-gray-50 rounded-lg border space-y-3">
          <h4 className="text-lg font-semibold">✨ AI Content Generator</h4>
          <input
            type="text"
            placeholder="Enter post topic..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
          <select value={selectedBrandVoice} onChange={(e) => setSelectedBrandVoice(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option value="" disabled>Select a Brand Voice</option>
            {brandVoices.map(bv => (
              <option key={bv.id} value={bv.id}>{bv.name}</option>
            ))}
          </select>
          <button type="button" onClick={handleGenerateContent} disabled={isGenerating} className="w-full px-4 py-2 font-semibold text-white bg-purple-600 rounded-md shadow-sm hover:bg-purple-700 disabled:bg-gray-400">
            {isGenerating ? 'Generating...' : 'Generate with AI'}
          </button>
        </div>
        
        {error && <div className="p-3 bg-red-100 text-red-700 rounded-md">{error}</div>}

        {/* Post Creation Form */}
        <form onSubmit={handleCreatePost} className="space-y-4">
          <select value={selectedAccount} onChange={(e) => setSelectedAccount(e.target.value)} required className="w-full px-3 py-2 border border-gray-300 rounded-md">
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
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
          <input
            type="text"
            placeholder="AI-generated image prompt will appear here..."
            value={imagePrompt}
            onChange={(e) => setImagePrompt(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
          
          <div className="p-3 bg-gray-50 rounded-md min-h-[60px]">
            <p className="text-sm font-medium text-gray-700 mb-2">Generated Hashtags:</p>
            <div className="flex flex-wrap gap-2">
              {hashtags.length > 0 ? (
                hashtags.map((tag, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">{tag}</span>
                ))
              ) : (
                <p className="text-sm text-gray-500">Hashtags will appear here...</p>
              )}
            </div>
          </div>

          <button type="submit" className="w-full px-4 py-2 font-semibold text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700">
            Create & Schedule Post
          </button>
        </form>
      </div>

      {/* Right Column: List Card */}
      <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-bold mb-4">Scheduled & Draft Posts</h3>
        {posts.length > 0 ? (
          <ul className="space-y-4">
            {posts.map((post) => (
              <li key={post.id} className={`p-4 rounded-lg border ${post.status === 'draft' ? 'bg-yellow-50' : 'bg-green-50'}`}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="text-sm text-gray-800">{post.content}</p>
                    {post.hashtags && post.hashtags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {post.hashtags.map((tag, index) => (
                          <span key={index} className="px-2 py-1 bg-gray-200 text-gray-700 text-xs font-semibold rounded-full">{tag}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="ml-4 text-right">
                    <span className={`px-2 py-1 text-xs font-bold rounded-full ${post.status === 'draft' ? 'bg-yellow-200 text-yellow-800' : 'bg-green-200 text-green-800'}`}>
                      {post.status}
                    </span>
                    <p className="text-xs text-gray-500 mt-1">{post.account_name}</p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>No posts found. Use the form on the left to create one.</p>
        )}
      </div>
    </div>
  );
}

export default SocialMediaManager;
