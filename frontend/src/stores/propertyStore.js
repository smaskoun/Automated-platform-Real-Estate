import { useSyncExternalStore } from 'react';
import realtorScrapingService from '../services/realtorScrapingService';

const CACHE_KEY = 'windsorEssexPropertiesCache';

const defaultState = {
  properties: [],
  loading: false,
  error: null,
  lastUpdated: null,
  filters: {
    searchQuery: '',
    minPrice: null,
    maxPrice: null,
    bedrooms: null,
    bathrooms: null,
    propertyTypes: [],
    municipalities: [],
  },
};

function createPropertyStore() {
  let state = { ...defaultState };
  const listeners = new Set();

  const notify = () => {
    listeners.forEach((listener) => listener(state));
  };

  const setState = (partial) => {
    const partialState =
      typeof partial === 'function' ? partial(state) : partial;

    state = {
      ...state,
      ...partialState,
    };

    notify();
  };

  const getState = () => state;

  const subscribe = (listener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  };

  const persistToCache = (payload) => {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    try {
      window.localStorage.setItem(CACHE_KEY, JSON.stringify(payload));
    } catch (storageError) {
      console.warn('Failed to persist property cache', storageError);
    }
  };

  const loadFromCache = () => {
    if (typeof window === 'undefined' || !window.localStorage) {
      return null;
    }

    try {
      const cachedRaw = window.localStorage.getItem(CACHE_KEY);

      if (!cachedRaw) {
        return null;
      }

      const cached = JSON.parse(cachedRaw);

      setState({
        properties: cached.properties ?? [],
        lastUpdated: cached.lastUpdated ?? null,
        loading: false,
      });

      return cached;
    } catch (cacheError) {
      setState({
        loading: false,
        error: 'Failed to load cached property data.',
      });

      return null;
    }
  };

  const fetchProperties = async () => {
    setState({ loading: true, error: null });

    try {
      const response = await realtorScrapingService.scrapeWindsorEssexProperties();

      const properties = Array.isArray(response)
        ? response
        : response?.properties ?? [];
      const lastUpdated =
        response?.lastUpdated ?? new Date().toISOString();

      const payload = { properties, lastUpdated };

      persistToCache(payload);

      setState({
        properties,
        loading: false,
        error: null,
        lastUpdated,
      });

      return properties;
    } catch (fetchError) {
      const cached = loadFromCache();

      if (cached?.properties?.length) {
        setState({
          loading: false,
          error:
            'Unable to refresh properties. Showing the most recent cached results.',
        });

        return cached.properties;
      }

      setState({
        properties: [],
        loading: false,
        error:
          fetchError?.message ?? 'Failed to fetch property data. Please try again later.',
      });

      return [];
    }
  };

  const setFilters = (updates) => {
    setState((current) => ({
      filters: {
        ...current.filters,
        ...updates,
      },
    }));
  };

  const matchesText = (haystack, needle) => {
    if (!needle) {
      return true;
    }

    return haystack.toLowerCase().includes(needle.toLowerCase());
  };

  const getFilteredProperties = () => {
    const { properties, filters } = getState();
    const {
      searchQuery,
      minPrice,
      maxPrice,
      bedrooms,
      bathrooms,
      propertyTypes,
      municipalities,
    } = filters;

    return properties.filter((property) => {
      if (
        searchQuery &&
        !matchesText(
          `${property.title ?? ''} ${property.address ?? ''} ${property.description ?? ''}`,
          searchQuery,
        )
      ) {
        return false;
      }

      const price =
        typeof property.price === 'number'
          ? property.price
          : typeof property.listPrice === 'number'
            ? property.listPrice
            : null;

      if (typeof minPrice === 'number' && price !== null && price < minPrice) {
        return false;
      }

      if (typeof maxPrice === 'number' && price !== null && price > maxPrice) {
        return false;
      }

      if (typeof bedrooms === 'number') {
        const propertyBedrooms =
          property.bedrooms ?? property.beds ?? property.bedroomsTotal ?? null;

        if (
          propertyBedrooms !== null &&
          Number(propertyBedrooms) < Number(bedrooms)
        ) {
          return false;
        }
      }

      if (typeof bathrooms === 'number') {
        const propertyBathrooms =
          property.bathrooms ?? property.baths ?? property.bathroomsTotal ?? null;

        if (
          propertyBathrooms !== null &&
          Number(propertyBathrooms) < Number(bathrooms)
        ) {
          return false;
        }
      }

      if (Array.isArray(propertyTypes) && propertyTypes.length > 0) {
        const propertyType = `${property.propertyType ?? property.type ?? ''}`.toLowerCase();

        if (
          !propertyTypes.some(
            (candidate) =>
              candidate && propertyType.includes(`${candidate}`.toLowerCase()),
          )
        ) {
          return false;
        }
      }

      if (Array.isArray(municipalities) && municipalities.length > 0) {
        const municipality = `${
          property.municipality ?? property.city ?? property.area ?? ''
        }`.toLowerCase();

        if (
          municipality &&
          !municipalities.some((candidate) =>
            municipality.includes(`${candidate}`.toLowerCase()),
          )
        ) {
          return false;
        }
      }

      return true;
    });
  };

  const clearError = () => {
    setState({ error: null });
  };

  const refreshProperties = () => fetchProperties();

  return {
    subscribe,
    getState,
    fetchProperties,
    loadFromCache,
    setFilters,
    getFilteredProperties,
    clearError,
    refreshProperties,
  };
}

const propertyStore = createPropertyStore();

export const usePropertyStore = () => {
  const state = useSyncExternalStore(
    propertyStore.subscribe,
    propertyStore.getState,
    propertyStore.getState,
  );

  return {
    ...state,
    fetchProperties: propertyStore.fetchProperties,
    loadFromCache: propertyStore.loadFromCache,
    setFilters: propertyStore.setFilters,
    getFilteredProperties: propertyStore.getFilteredProperties,
    clearError: propertyStore.clearError,
    refreshProperties: propertyStore.refreshProperties,
  };
};

export default usePropertyStore;
