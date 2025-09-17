import React, { useEffect, useState } from 'react';
import api from './api.js';
import { useKeywordSets } from './KeywordSetsContext.jsx';

function SeoTools({
  initialSavedBundles,
  onBundlesChange = () => {},
  onBundleSelected = () => {},
}) {
  const [keywordInput, setKeywordInput] = useState('');
  const [keywordSetName, setKeywordSetName] = useState('');
  const [hashtagInput, setHashtagInput] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [selectedKeywords, setSelectedKeywords] = useState([]);
  const [savedBundles, setSavedBundles] = useState(() => initialSavedBundles ?? []);
  const [bundleName, setBundleName] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [saveMessage, setSaveMessage] = useState('');
  const { savedKeywordSets, addKeywordSet, removeKeywordSet } = useKeywordSets();

  useEffect(() => {
    if (initialSavedBundles === undefined) {
      return;
    }
    setSavedBundles(initialSavedBundles);
  }, [initialSavedBundles]);

  useEffect(() => {
    onBundlesChange(savedBundles);
  }, [savedBundles, onBundlesChange]);

  useEffect(() => {
    if (!statusMessage) {
      return undefined;
    }
    const timeoutId = setTimeout(() => setStatusMessage(''), 3000);
    return () => clearTimeout(timeoutId);
  }, [statusMessage]);

  const handleAnalyze = async () => {
    const keywords = keywordInput.split(',').map((k) => k.trim()).filter(Boolean);
    if (keywords.length === 0) {
      setError('Please enter at least one keyword.');
      setAnalysis(null);
      setSelectedKeywords([]);
      return;
    }
    setError('');
    try {
      const response = await api.post('/api/seo/analyze-keywords', { keywords });
      setAnalysis(response.data);
      setSelectedKeywords([]);
      setStatusMessage('');
    } catch (err) {
      console.error('Keyword analysis failed:', err);
      setError('Failed to analyze keywords.');
      setAnalysis(null);
      setSelectedKeywords([]);
    }
  };

  const toggleKeyword = (keyword) => {
    setSelectedKeywords((prev) => (
      prev.includes(keyword)
        ? prev.filter((k) => k !== keyword)
        : [...prev, keyword]
    ));
  };

  const addKeywordsToSelection = (keywordsToAdd) => {
    const normalized = Array.isArray(keywordsToAdd) ? keywordsToAdd : [keywordsToAdd];
    setSelectedKeywords((prev) => {
      const unique = new Set(prev);
      normalized.forEach((keyword) => {
        if (keyword) {
          unique.add(keyword);
        }
      });
      return Array.from(unique);
    });
  };

  const handleClearSelected = () => {
    setSelectedKeywords([]);
  };

  const copyTextToClipboard = async (text) => {
    if (!text) {
      return;
    }
    if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
    if (typeof document !== 'undefined') {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.setAttribute('readonly', '');
      textarea.style.position = 'absolute';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return;
    }
    throw new Error('Clipboard API is not available.');
  };

  const handleCopyKeywords = async (keywordsToCopy) => {
    const normalized = Array.isArray(keywordsToCopy) ? keywordsToCopy : [keywordsToCopy];
    const filtered = normalized.map((keyword) => keyword && keyword.trim()).filter(Boolean);
    if (filtered.length === 0) {
      setError('There are no keywords to copy.');
      return;
    }
    try {
      await copyTextToClipboard(filtered.join(', '));
      setError('');
      setStatusMessage('Keywords copied to clipboard.');
    } catch (err) {
      console.error('Copy failed:', err);
      setError('Failed to copy keywords.');
    }
  };

  const handleSaveBundle = () => {
    if (selectedKeywords.length === 0) {
      setError('Select at least one keyword before saving.');
      return;
    }
    const normalizedKeywords = Array.from(new Set(selectedKeywords));
    const name = bundleName.trim() || `Bundle ${savedBundles.length + 1}`;
    const newBundle = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      name,
      keywords: normalizedKeywords,
    };
    setSavedBundles((prev) => [newBundle, ...prev]);
    setBundleName('');
    setStatusMessage(`Saved "${name}".`);
    setError('');
  };

  const handleLoadBundle = (bundle) => {
    if (!bundle) {
      return;
    }
    setSelectedKeywords(bundle.keywords);
    setKeywordInput(bundle.keywords.join(', '));
    setStatusMessage(`Loaded "${bundle.name}".`);
    setError('');
    onBundleSelected(bundle);
  };

  const handleSelectAllSuggestions = () => {
    if (!analysis || !analysis.suggestions) {
      return;
    }
    addKeywordsToSelection(analysis.suggestions);
  };

  const handleSelectAllScoreKeywords = () => {
    if (!analysis || !analysis.scores) {
      return;
    }
    addKeywordsToSelection(Object.keys(analysis.scores));
  };

  const handleSaveKeywordSet = () => {
    const keywords = keywordInput.split(',').map((k) => k.trim()).filter(Boolean);
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
      {error && <div className="text-red-600">{error}</div>}
      {statusMessage && <div className="text-green-600">{statusMessage}</div>}

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
        <div className="space-y-6">
          <div>
            <h3 className="font-semibold">Normalized Keywords</h3>
            <p className="text-sm text-gray-700">{(analysis.input || []).join(', ')}</p>
          </div>
          <div>
            <h3 className="font-semibold">Suggestions</h3>
            {(analysis.suggestions || []).length > 0 ? (
              <div className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  {analysis.suggestions.map((suggestion, idx) => {
                    const isSelected = selectedKeywords.includes(suggestion);
                    return (
                      <div key={`${suggestion}-${idx}`} className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => toggleKeyword(suggestion)}
                          className={`px-3 py-1 rounded-full border text-sm transition-colors ${
                            isSelected
                              ? 'bg-blue-100 border-blue-500 text-blue-700'
                              : 'bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {suggestion}
                        </button>
                        <button
                          type="button"
                          onClick={() => handleCopyKeywords(suggestion)}
                          className="text-xs font-medium text-blue-600 hover:underline"
                        >
                          Copy
                        </button>
                      </div>
                    );
                  })}
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => handleCopyKeywords(analysis.suggestions)}
                    className="px-3 py-1 text-sm font-medium border border-gray-300 rounded-md hover:bg-gray-100"
                  >
                    Copy All Suggestions
                  </button>
                  <button
                    type="button"
                    onClick={handleSelectAllSuggestions}
                    className="px-3 py-1 text-sm font-medium border border-gray-300 rounded-md hover:bg-gray-100"
                  >
                    Select All Suggestions
                  </button>
                </div>
              </div>
            ) : (
              <p>No suggestions available.</p>
            )}
          </div>
          <div>
            <h3 className="font-semibold">Scores</h3>
            {Object.keys(analysis.scores || {}).length > 0 ? (
              <div className="space-y-3">
                <div className="space-y-2">
                  {Object.entries(analysis.scores || {}).map(([kw, score]) => {
                    const isSelected = selectedKeywords.includes(kw);
                    return (
                      <div
                        key={kw}
                        className="flex flex-wrap items-center justify-between gap-2 border border-gray-200 rounded-md px-3 py-2"
                      >
                        <div className="flex items-center gap-3">
                          <button
                            type="button"
                            onClick={() => toggleKeyword(kw)}
                            className={`px-3 py-1 rounded-full border text-sm transition-colors ${
                              isSelected
                                ? 'bg-blue-100 border-blue-500 text-blue-700'
                                : 'bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200'
                            }`}
                          >
                            {kw}
                          </button>
                          <span className="text-sm text-gray-600">Score: {score}</span>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleCopyKeywords(kw)}
                          className="text-xs font-medium text-blue-600 hover:underline"
                        >
                          Copy
                        </button>
                      </div>
                    );
                  })}
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => handleCopyKeywords(Object.keys(analysis.scores || {}))}
                    className="px-3 py-1 text-sm font-medium border border-gray-300 rounded-md hover:bg-gray-100"
                  >
                    Copy All Score Keywords
                  </button>
                  <button
                    type="button"
                    onClick={handleSelectAllScoreKeywords}
                    className="px-3 py-1 text-sm font-medium border border-gray-300 rounded-md hover:bg-gray-100"
                  >
                    Select All Score Keywords
                  </button>
                </div>
              </div>
            ) : (
              <p>No scores available.</p>
            )}
          </div>
          <div>
            <h3 className="font-semibold">Selected Keywords</h3>
            {selectedKeywords.length > 0 ? (
              <div className="mt-2 flex flex-wrap gap-2">
                {selectedKeywords.map((keyword) => (
                  <span
                    key={keyword}
                    className="inline-flex items-center gap-2 px-3 py-1 text-sm rounded-full bg-blue-100 text-blue-700"
                  >
                    {keyword}
                    <button
                      type="button"
                      onClick={() => toggleKeyword(keyword)}
                      className="text-xs font-semibold text-blue-600 hover:underline"
                    >
                      Remove
                    </button>
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No keywords selected yet.</p>
            )}
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => handleCopyKeywords(selectedKeywords)}
                disabled={selectedKeywords.length === 0}
                className="px-3 py-1 text-sm font-medium border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                Copy Selected Keywords
              </button>
              <button
                type="button"
                onClick={handleClearSelected}
                disabled={selectedKeywords.length === 0}
                className="px-3 py-1 text-sm font-medium border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                Clear Selection
              </button>
            </div>
            <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center">
              <input
                type="text"
                value={bundleName}
                onChange={(e) => setBundleName(e.target.value)}
                placeholder="Name this bundle"
                className="w-full sm:flex-1 px-3 py-2 border border-gray-300 rounded-md"
              />
              <button
                type="button"
                onClick={handleSaveBundle}
                disabled={selectedKeywords.length === 0}
                className="px-4 py-2 text-sm font-semibold text-white bg-green-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-green-700"
              >
                Save Selected Keywords
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-3">
        <h3 className="font-semibold">Saved Keyword Bundles</h3>
        {savedBundles.length > 0 ? (
          <ul className="space-y-3">
            {savedBundles.map((bundle) => (
              <li key={bundle.id} className="border border-gray-200 rounded-md p-3">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium">{bundle.name}</p>
                    <p className="text-sm text-gray-600 break-words">{bundle.keywords.join(', ')}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => handleCopyKeywords(bundle.keywords)}
                      className="px-3 py-1 text-sm font-medium border border-gray-300 rounded-md hover:bg-gray-100"
                    >
                      Copy
                    </button>
                    <button
                      type="button"
                      onClick={() => handleLoadBundle(bundle)}
                      className="px-3 py-1 text-sm font-medium border border-gray-300 rounded-md hover:bg-gray-100"
                    >
                      Load
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500">No saved bundles yet. Save selections to reuse them later.</p>
        )}
      </div>
    </div>
  );
}

export default SeoTools;

