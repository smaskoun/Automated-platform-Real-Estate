import React, { useEffect, useState } from 'react';
import api from './api.js';
import { useKeywordSets } from './KeywordSetsContext.jsx';
import styles from './SeoTools.module.css';

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
    <div className={styles.container}>
      <h2 className={styles.title}>SEO Keyword Analyzer</h2>
      {error && <div className={`${styles.message} ${styles.error}`}>{error}</div>}
      {statusMessage && <div className={`${styles.message} ${styles.status}`}>{statusMessage}</div>}

      <div className={styles.grid}>
        <section className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>Discover High-Impact Keywords</h3>
            <p className={styles.cardSubtitle}>
              Run analysis on your seed keywords, capture hashtags, and save bundles for later.
            </p>
          </div>
          <div className={styles.inputGrid}>
            <div className={styles.inputGroup}>
              <label htmlFor="keywordInput">Keywords</label>
              <input
                id="keywordInput"
                type="text"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                placeholder="Enter keywords separated by commas"
                className={styles.textInput}
              />
            </div>
            <div className={styles.inputGroup}>
              <label htmlFor="hashtagInput">Optional Hashtags</label>
              <input
                id="hashtagInput"
                type="text"
                value={hashtagInput}
                onChange={(e) => setHashtagInput(e.target.value)}
                placeholder="Comma-separated hashtags"
                className={styles.textInput}
              />
            </div>
            <div className={styles.inputGroup}>
              <label htmlFor="keywordSetName">Name this keyword set</label>
              <div className={styles.buttonRow}>
                <input
                  id="keywordSetName"
                  type="text"
                  value={keywordSetName}
                  onChange={(e) => setKeywordSetName(e.target.value)}
                  placeholder="e.g., Spring Listings Push"
                  className={styles.textInput}
                />
                <button type="button" onClick={handleSaveKeywordSet} className={styles.secondaryButton}>
                  Save for Social Media
                </button>
              </div>
              {saveMessage && <span className={styles.savedMessage}>{saveMessage}</span>}
            </div>
            <div className={styles.actionRow}>
              <button type="button" onClick={handleAnalyze} className={styles.primaryButton}>
                Analyze Keywords
              </button>
            </div>
          </div>
        </section>

        <aside className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>Saved Keyword Sets</h3>
            <p className={styles.cardSubtitle}>Quickly reuse sets in the Social Media Manager.</p>
          </div>
          <div className={styles.keywordSetsCard}>
            {savedKeywordSets.length === 0 ? (
              <p className={styles.emptyState}>No keyword sets saved yet.</p>
            ) : (
              savedKeywordSets.map((set) => (
                <div key={set.id} className={styles.keywordSetItem}>
                  <div className={styles.keywordSetMeta}>
                    <p>{set.name}</p>
                    {set.primaryKeyword && <span>Primary: {set.primaryKeyword}</span>}
                    {set.hashtags?.length > 0 && <span>Hashtags: {set.hashtags.join(', ')}</span>}
                    {set.keywords?.length > 0 && <span>Keywords: {set.keywords.join(', ')}</span>}
                  </div>
                  <div className={styles.keywordSetActions}>
                    <button type="button" className={styles.linkButton} onClick={() => handleRemoveSet(set.id)}>
                      Remove
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </aside>
      </div>

      {analysis && (
        <section className={styles.resultsCard}>
          <div>
            <h3 className={styles.sectionTitle}>Normalized Keywords</h3>
            <p className={styles.sectionText}>{(analysis.input || []).join(', ')}</p>
          </div>

          <div>
            <h3 className={styles.sectionTitle}>Suggestions</h3>
            {(analysis.suggestions || []).length > 0 ? (
              <>
                <div className={styles.chipList}>
                  {analysis.suggestions.map((suggestion, idx) => {
                    const isSelected = selectedKeywords.includes(suggestion);
                    return (
                      <div key={`${suggestion}-${idx}`} className={`${styles.chip} ${isSelected ? styles.chipActive : ''}`}>
                        <span>{suggestion}</span>
                        <div className={styles.chipActions}>
                          <button type="button" className={styles.linkButton} onClick={() => toggleKeyword(suggestion)}>
                            {isSelected ? 'Remove' : 'Select'}
                          </button>
                          <button type="button" className={styles.linkButton} onClick={() => handleCopyKeywords(suggestion)}>
                            Copy
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className={styles.actionRow}>
                  <button
                    type="button"
                    onClick={() => handleCopyKeywords(analysis.suggestions)}
                    className={styles.secondaryButton}
                  >
                    Copy All Suggestions
                  </button>
                  <button type="button" onClick={handleSelectAllSuggestions} className={styles.secondaryButton}>
                    Select All Suggestions
                  </button>
                </div>
              </>
            ) : (
              <p className={styles.sectionText}>No suggestions available.</p>
            )}
          </div>

          <div>
            <h3 className={styles.sectionTitle}>Scores</h3>
            {Object.keys(analysis.scores || {}).length > 0 ? (
              <>
                <div className={styles.inputGrid}>
                  {Object.entries(analysis.scores || {}).map(([kw, score]) => {
                    const isSelected = selectedKeywords.includes(kw);
                    return (
                      <div key={kw} className={styles.scoreRow}>
                        <div className={styles.chipActions}>
                          <div className={`${styles.chip} ${isSelected ? styles.chipActive : ''}`}>
                            <span>{kw}</span>
                            <button type="button" className={styles.linkButton} onClick={() => toggleKeyword(kw)}>
                              {isSelected ? 'Remove' : 'Select'}
                            </button>
                          </div>
                        </div>
                        <span>Score: {score}</span>
                        <button type="button" className={styles.linkButton} onClick={() => handleCopyKeywords(kw)}>
                          Copy
                        </button>
                      </div>
                    );
                  })}
                </div>
                <div className={styles.actionRow}>
                  <button
                    type="button"
                    onClick={() => handleCopyKeywords(Object.keys(analysis.scores || {}))}
                    className={styles.secondaryButton}
                  >
                    Copy All Score Keywords
                  </button>
                  <button type="button" onClick={handleSelectAllScoreKeywords} className={styles.secondaryButton}>
                    Select All Score Keywords
                  </button>
                </div>
              </>
            ) : (
              <p className={styles.sectionText}>No scores available.</p>
            )}
          </div>

          <div>
            <h3 className={styles.sectionTitle}>Selected Keywords</h3>
            {selectedKeywords.length > 0 ? (
              <div className={styles.selectedChips}>
                {selectedKeywords.map((keyword) => (
                  <div key={keyword} className={`${styles.chip} ${styles.chipActive}`}>
                    <span>{keyword}</span>
                    <button type="button" className={styles.linkButton} onClick={() => toggleKeyword(keyword)}>
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className={styles.sectionText}>No keywords selected yet.</p>
            )}
            <div className={styles.actionRow}>
              <button
                type="button"
                onClick={() => handleCopyKeywords(selectedKeywords)}
                disabled={selectedKeywords.length === 0}
                className={styles.secondaryButton}
              >
                Copy Selected Keywords
              </button>
              <button
                type="button"
                onClick={handleClearSelected}
                disabled={selectedKeywords.length === 0}
                className={styles.secondaryButton}
              >
                Clear Selection
              </button>
            </div>
            <div className={styles.buttonRow}>
              <input
                type="text"
                value={bundleName}
                onChange={(e) => setBundleName(e.target.value)}
                placeholder="Name this bundle"
                className={styles.textInput}
              />
              <button
                type="button"
                onClick={handleSaveBundle}
                disabled={selectedKeywords.length === 0}
                className={styles.primaryButton}
              >
                Save Selected Keywords
              </button>
            </div>
          </div>
        </section>
      )}

      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <h3 className={styles.cardTitle}>Saved Keyword Bundles</h3>
          <p className={styles.cardSubtitle}>Reuse curated collections without starting from scratch.</p>
        </div>
        {savedBundles.length > 0 ? (
          <ul className={styles.bundleList}>
            {savedBundles.map((bundle) => (
              <li key={bundle.id} className={styles.bundleItem}>
                <div className={styles.bundleMeta}>
                  <p>{bundle.name}</p>
                  <span>{bundle.keywords.join(', ')}</span>
                </div>
                <div className={styles.bundleActions}>
                  <button type="button" onClick={() => handleCopyKeywords(bundle.keywords)} className={styles.secondaryButton}>
                    Copy
                  </button>
                  <button type="button" onClick={() => handleLoadBundle(bundle)} className={styles.primaryButton}>
                    Load
                  </button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.emptyState}>No saved bundles yet. Save selections to reuse them later.</p>
        )}
      </section>
    </div>
  );
}

export default SeoTools;
