import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

const KeywordSetsContext = createContext(null);
const STORAGE_KEY = 'seo-keyword-sets';

function normalizeHashtag(value) {
  if (!value) return '';
  const cleaned = value
    .toString()
    .trim()
    .replace(/[#\s]+/g, ' ')
    .split(' ')
    .filter(Boolean)
    .join('');

  if (!cleaned) {
    return '';
  }

  return `#${cleaned}`;
}

export function KeywordSetsProvider({ children }) {
  const [savedKeywordSets, setSavedKeywordSets] = useState(() => {
    if (typeof window === 'undefined') {
      return [];
    }
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (!stored) {
        return [];
      }
      const parsed = JSON.parse(stored);
      if (!Array.isArray(parsed)) {
        return [];
      }
      return parsed.map((set) => ({
        ...set,
        hashtags: Array.isArray(set?.hashtags)
          ? set.hashtags.filter(Boolean)
          : [],
        keywords: Array.isArray(set?.keywords)
          ? set.keywords.filter(Boolean)
          : [],
      }));
    } catch (err) {
      console.error('Failed to read stored keyword sets', err);
      return [];
    }
  });

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(savedKeywordSets));
    } catch (err) {
      console.error('Failed to persist keyword sets', err);
    }
  }, [savedKeywordSets]);

  const addKeywordSet = (payload) => {
    setSavedKeywordSets((prev) => {
      const keywords = Array.isArray(payload.keywords)
        ? payload.keywords.filter(Boolean)
        : [];
      const hashtags = Array.isArray(payload.hashtags)
        ? payload.hashtags.map(normalizeHashtag).filter(Boolean)
        : [];
      const primaryKeyword = payload.primaryKeyword || keywords[0] || '';
      const next = {
        id: payload.id || `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        name: payload.name || primaryKeyword || 'Saved Keywords',
        keywords,
        primaryKeyword,
        hashtags,
      };

      const filtered = prev.filter((set) => set.id !== next.id && set.name !== next.name);
      return [...filtered, next];
    });
  };

  const removeKeywordSet = (id) => {
    setSavedKeywordSets((prev) => prev.filter((set) => set.id !== id));
  };

  const value = useMemo(
    () => ({
      savedKeywordSets,
      addKeywordSet,
      removeKeywordSet,
    }),
    [savedKeywordSets],
  );

  return (
    <KeywordSetsContext.Provider value={value}>
      {children}
    </KeywordSetsContext.Provider>
  );
}

export function useKeywordSets() {
  const context = useContext(KeywordSetsContext);
  if (!context) {
    throw new Error('useKeywordSets must be used within a KeywordSetsProvider');
  }
  return context;
}

export default KeywordSetsContext;
