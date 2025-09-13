import React, { useState } from 'react';
import api from './api.js';

function SeoTools() {
  const [keywordInput, setKeywordInput] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');

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

  return (
    <div className="max-w-xl mx-auto bg-white p-6 rounded-lg shadow-md space-y-4">
      <h2 className="text-2xl font-bold">SEO Keyword Analyzer</h2>
      <input
        type="text"
        value={keywordInput}
        onChange={(e) => setKeywordInput(e.target.value)}
        placeholder="Enter keywords separated by commas"
        className="w-full px-3 py-2 border border-gray-300 rounded-md"
      />
      <button
        type="button"
        onClick={handleAnalyze}
        className="px-4 py-2 font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700"
      >
        Analyze
      </button>
      {error && <div className="text-red-600">{error}</div>}
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

