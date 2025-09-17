import React, { useState } from 'react';
import api from './api.js';
import { useKeywordSets } from './KeywordSetsContext.jsx';

function SeoTools() {
  const [keywordInput, setKeywordInput] = useState('');
  const [keywordSetName, setKeywordSetName] = useState('');
  const [hashtagInput, setHashtagInput] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [saveMessage, setSaveMessage] = useState('');
  const { savedKeywordSets, addKeywordSet, removeKeywordSet } = useKeywordSets();

  const handleAnalyze = async () => {
    const keywords = keywordInput.split(',').map(k => k.trim()).filter(Boolean);
    if (keywords.length === 0) {
      setError('Please enter at least one keyword.');
      setAnalysis(null);
      return;
    }
    setError('');
    try {
      const response = await api.post('/api/seo/analyze-keywords', { keywords });
      setAnalysis(response.data);
    } catch (err) {
      console.error('Keyword analysis failed:', err);
      setError('Failed to analyze keywords.');
      setAnalysis(null);
    }
  };

  const handleSaveKeywordSet = () => {
    const keywords = keywordInput.split(',').map(k => k.trim()).filter(Boolean);
    if (keywords.length === 0) {
      setError('Please enter keywords before saving.');
      return;
    }

    const hashtags = hashtagInput
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean);

    addKeywordSet({
      name: keywordSetName.trim() || keywords[0],
      keywords,
      primaryKeyword: keywords[0],
      hashtags: hashtags.length > 0 ? hashtags : keywords.slice(1),
    });

    setError('');
    setKeywordSetName('');
    setHashtagInput('');
    setSaveMessage('Keyword set saved for Social Media Manager.');
    setTimeout(() => setSaveMessage(''), 2500);
  };

  const handleRemoveSet = (id) => {
    removeKeywordSet(id);
  };

  return (
    <div className="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow-md space-y-6">
      <h2 className="text-2xl font-bold">SEO Keyword Analyzer</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <input
            type="text"
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
            placeholder="Enter keywords separated by commas"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
          <input
            type="text"
            value={hashtagInput}
            onChange={(e) => setHashtagInput(e.target.value)}
            placeholder="Optional hashtags (comma separated)"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
          <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-3 space-y-3 sm:space-y-0">
            <input
              type="text"
              value={keywordSetName}
              onChange={(e) => setKeywordSetName(e.target.value)}
              placeholder="Name this keyword set"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
            />
            <button
              type="button"
              onClick={handleSaveKeywordSet}
              className="px-4 py-2 font-semibold text-white bg-green-600 rounded-md hover:bg-green-700"
            >
              Save for Social Media
            </button>
          </div>
          <button
            type="button"
            onClick={handleAnalyze}
            className="px-4 py-2 font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Analyze
          </button>
          {saveMessage && <div className="text-green-600 text-sm">{saveMessage}</div>}
          {error && <div className="text-red-600">{error}</div>}
        </div>

        <div className="bg-gray-50 border rounded-lg p-4 space-y-3">
          <h3 className="text-lg font-semibold">Saved Keyword Sets</h3>
          {savedKeywordSets.length === 0 ? (
            <p className="text-sm text-gray-600">No keyword sets saved yet.</p>
          ) : (
            <ul className="space-y-3 max-h-64 overflow-y-auto">
              {savedKeywordSets.map((set) => (
                <li key={set.id} className="p-3 bg-white border rounded-md">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold">{set.name}</p>
                      <p className="text-sm text-gray-600">Primary: {set.primaryKeyword}</p>
                      {set.hashtags?.length > 0 && (
                        <p className="text-xs text-gray-500">Hashtags: {set.hashtags.join(', ')}</p>
                      )}
                      {set.keywords?.length > 0 && (
                        <p className="text-xs text-gray-500">Keywords: {set.keywords.join(', ')}</p>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveSet(set.id)}
                      className="text-sm text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      {analysis && (
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold">Normalized Keywords</h3>
            <p>{analysis.input.join(', ')}</p>
          </div>
          <div>
            <h3 className="font-semibold">Suggestions</h3>
            {analysis.suggestions.length > 0 ? (
              <ul className="list-disc list-inside">
                {analysis.suggestions.map((s, idx) => (
                  <li key={idx}>{s}</li>
                ))}
              </ul>
            ) : (
              <p>No suggestions available.</p>
            )}
          </div>
          <div>
            <h3 className="font-semibold">Scores</h3>
            <ul className="list-disc list-inside">
              {Object.entries(analysis.scores || {}).map(([kw, score]) => (
                <li key={kw}>{kw}: {score}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default SeoTools;

