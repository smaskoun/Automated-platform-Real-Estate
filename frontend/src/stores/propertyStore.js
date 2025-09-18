import { useSyncExternalStore } from 'react';
import realtorScrapingService from '../services/realtorScrapingService';

const CACHE_KEY = 'windsorEssexPropertiesCache';

const defaultFilters = {
  status: ['Active', 'Pending', 'Sold'],
  propertyType: 'all',
  priceSegment: 'all',
  featuredOnly: false,
  openHouseOnly: false,
  searchTerm: '',
  searchQuery: '',
  minPrice: null,
  maxPrice: null,
  bedrooms: null,
  bathrooms: null,
  propertyTypes: [],
  municipalities: [],
};

const defaultStatistics = {
  total: 0,
  active: 0,
  pending: 0,
  sold: 0,
  featured: 0,
  openHouses: 0,
  averagePrice: 0,
  averageDaysOnMarket: 0,
};

const defaultState = {
  properties: [],
  filters: { ...defaultFilters },
  statistics: { ...defaultStatistics },
  generatedContent: {},
  generationStatus: {},
  isLoading: false,
  loading: false,
  error: null,
  lastUpdated: null,
  dataSource: null,
  actions: {},
};

const delay = (ms) =>
  new Promise((resolve) => {
    setTimeout(resolve, ms);
  });

const safeString = (value) => {
  if (typeof value === 'string') {
    return value.trim();
  }

  if (value === null || value === undefined) {
    return '';
  }

  if (typeof value === 'number' && Number.isFinite(value)) {
    return `${value}`;
  }

  if (typeof value === 'object' && value?.toString) {
    return value.toString();
  }

  return '';
};

const toNumber = (value) => {
  if (value === null || value === undefined) {
    return null;
  }

  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null;
  }

  if (typeof value === 'string') {
    const normalized = value.replace(/[^0-9.,-]+/g, '');

    if (!normalized) {
      return null;
    }

    const match = normalized.match(/-?\d+(?:[.,]\d+)?/);

    if (!match) {
      return null;
    }

    const numericValue = Number(match[0].replace(/,/g, ''));

    return Number.isFinite(numericValue) ? numericValue : null;
  }

  return null;
};

const getPriceFromProperty = (raw = {}) => {
  const candidates = [
    raw.price,
    raw.listPrice,
    raw.priceValue,
    raw.priceAmount,
    raw.originalPrice,
    raw.expectedPrice,
    raw.minimumPrice,
  ];

  for (const candidate of candidates) {
    const numeric = toNumber(candidate);
    if (numeric !== null) {
      return numeric;
    }
  }

  return null;
};

const buildTags = (details = {}) => {
  const tags = new Set();

  if (details.propertyType) {
    tags.add(details.propertyType);
  }

  if (details.city) {
    tags.add(details.city);
  }

  if (details.neighbourhood) {
    tags.add(details.neighbourhood);
  }

  const bedrooms = toNumber(details.bedrooms);
  if (bedrooms !== null) {
    tags.add(`${bedrooms} bd`);
  }

  const bathrooms = toNumber(details.bathrooms);
  if (bathrooms !== null) {
    tags.add(`${bathrooms} ba`);
  }

  const area = toNumber(details.area ?? details.squareFeet);
  if (area !== null) {
    try {
      tags.add(`${Number(area).toLocaleString()} sq ft`);
    } catch (error) {
      tags.add(`${area} sq ft`);
    }
  }

  return Array.from(tags).filter(Boolean);
};

const extractOverview = (text) => {
  if (typeof text !== 'string') {
    return null;
  }

  const cleaned = text.replace(/\s+/g, ' ').trim();

  if (!cleaned) {
    return null;
  }

  const sentences = cleaned
    .split(/[.!?]/)
    .map((sentence) => sentence.trim())
    .filter(Boolean);

  return sentences[0] ?? cleaned;
};

const buildHighlights = (details = {}) => {
  const highlights = [];

  const overview = extractOverview(details.description);
  if (overview) {
    highlights.push({ label: 'Overview', value: overview });
  }

  if (details.lotSizeText) {
    highlights.push({ label: 'Lot size', value: details.lotSizeText });
  }

  const yearBuilt = toNumber(details.yearBuilt);
  if (yearBuilt !== null) {
    highlights.push({ label: 'Year built', value: `${yearBuilt}` });
  }

  if (details.propertyType && details.city) {
    highlights.push({ label: 'Location', value: `${details.propertyType} in ${details.city}` });
  }

  return highlights.slice(0, 3);
};

const buildMetrics = (raw = {}) => {
  const source = raw.metrics ?? {};

  const daysOnMarket =
    toNumber(source.daysOnMarket) ?? toNumber(raw.daysOnMarket) ?? toNumber(raw.dom) ?? 0;

  return {
    daysOnMarket: daysOnMarket ?? 0,
    views: toNumber(source.views) ?? 0,
    saves: toNumber(source.saves) ?? 0,
    inquiries: toNumber(source.inquiries) ?? 0,
  };
};

const ensurePropertyShape = (property) => {
  if (!property || typeof property !== 'object') {
    return null;
  }

  const normalized = { ...property };

  const idCandidate =
    normalized.id ??
    normalized.mlsNumber ??
    normalized.listingId ??
    normalized.mlsId ??
    normalized.propertyId ??
    normalized.listingUrl ??
    normalized.address;

  normalized.id =
    idCandidate && `${idCandidate}`.trim()
      ? `${idCandidate}`
      : `property-${Math.random().toString(36).slice(2, 10)}`;

  normalized.title =
    typeof normalized.title === 'string' && normalized.title.trim()
      ? normalized.title.trim()
      : normalized.address || 'Property listing';

  normalized.status = normalized.status || 'Active';

  const price = toNumber(normalized.price);
  normalized.price = price !== null ? price : getPriceFromProperty(normalized);

  if (typeof normalized.price === 'number' && Number.isFinite(normalized.price)) {
    try {
      normalized.priceFormatted =
        normalized.priceFormatted ??
        new Intl.NumberFormat('en-CA', {
          style: 'currency',
          currency: 'CAD',
          maximumFractionDigits: 0,
        }).format(normalized.price);
    } catch (error) {
      normalized.priceFormatted = normalized.priceFormatted ?? null;
    }
  } else {
    normalized.price = null;
  }

  normalized.address =
    typeof normalized.address === 'string' && normalized.address.trim()
      ? normalized.address.trim()
      : null;

  normalized.city =
    typeof normalized.city === 'string' && normalized.city.trim()
      ? normalized.city.trim()
      : normalized.municipality
        ? safeString(normalized.municipality) || null
        : null;

  normalized.neighbourhood =
    typeof normalized.neighbourhood === 'string' && normalized.neighbourhood.trim()
      ? normalized.neighbourhood.trim()
      : normalized.city;

  normalized.propertyType =
    typeof normalized.propertyType === 'string' && normalized.propertyType.trim()
      ? normalized.propertyType.trim()
      : 'Property';

  normalized.bedrooms = toNumber(normalized.bedrooms);
  normalized.bathrooms = toNumber(normalized.bathrooms);
  normalized.area = toNumber(normalized.area ?? normalized.squareFeet);

  normalized.tags = Array.isArray(normalized.tags)
    ? normalized.tags.filter(Boolean)
    : [];

  if (!normalized.tags.length) {
    normalized.tags = buildTags({
      propertyType: normalized.propertyType,
      city: normalized.city,
      neighbourhood: normalized.neighbourhood,
      bedrooms: normalized.bedrooms,
      bathrooms: normalized.bathrooms,
      area: normalized.area,
    });
  }

  normalized.highlights = Array.isArray(normalized.highlights)
    ? normalized.highlights
        .map((entry) =>
          entry && typeof entry === 'object' && entry.label && entry.value
            ? { label: entry.label, value: entry.value }
            : null,
        )
        .filter(Boolean)
    : [];

  if (!normalized.highlights.length) {
    normalized.highlights = buildHighlights({
      description: normalized.description,
      lotSizeText: normalized.lotSizeText,
      yearBuilt: normalized.yearBuilt,
      propertyType: normalized.propertyType,
      city: normalized.city,
      neighbourhood: normalized.neighbourhood,
    });
  }

  normalized.metrics = {
    daysOnMarket: toNumber(normalized.metrics?.daysOnMarket) ?? 0,
    views: toNumber(normalized.metrics?.views) ?? 0,
    saves: toNumber(normalized.metrics?.saves) ?? 0,
    inquiries: toNumber(normalized.metrics?.inquiries) ?? 0,
  };

  normalized.featured = Boolean(normalized.featured);
  normalized.openHouse = Boolean(normalized.openHouse);
  normalized.listedAt = normalized.listedAt ?? null;
  normalized.description =
    typeof normalized.description === 'string' ? normalized.description : null;

  normalized.images = Array.isArray(normalized.images) ? normalized.images : [];
  normalized.agents = Array.isArray(normalized.agents) ? normalized.agents : [];
  normalized.coordinates = normalized.coordinates ?? null;
  normalized.brokerage =
    typeof normalized.brokerage === 'string' && normalized.brokerage.trim()
      ? normalized.brokerage.trim()
      : null;

  return normalized;
};

const normalizeProperty = (raw) => {
  if (!raw || typeof raw !== 'object') {
    return null;
  }

  const normalized = {
    id:
      raw.id ||
      raw.mlsNumber ||
      raw.listingId ||
      raw.mlsId ||
      raw.property?.id ||
      raw.property?.mlsNumber ||
      raw.listingUrl ||
      raw.address ||
      null,
    title:
      (typeof raw.title === 'string' && raw.title.trim()) ||
      safeString(raw.address) ||
      (raw.mlsNumber ? `MLS ${raw.mlsNumber}` : null),
    status: raw.status || raw.listingStatus || raw.saleStatus || 'Active',
    price: getPriceFromProperty(raw),
    priceFormatted: raw.priceFormatted || raw.priceText || raw.displayPrice || null,
    address: raw.address ?? raw.location?.address ?? null,
    neighbourhood:
      raw.neighbourhood ||
      raw.community ||
      raw.subdivision ||
      raw.areaName ||
      raw.location?.neighbourhood ||
      null,
    municipality: raw.municipality || raw.city || raw.location?.municipality || null,
    city: raw.city || raw.location?.city || raw.municipality || null,
    province: raw.province || raw.location?.province || null,
    postalCode: raw.postalCode || raw.location?.postalCode || null,
    propertyType:
      raw.propertyType ||
      raw.type ||
      raw.property?.type ||
      raw.building?.type ||
      raw.category ||
      null,
    bedrooms: raw.bedrooms ?? raw.summary?.bedrooms ?? raw.building?.bedrooms ?? null,
    bathrooms: raw.bathrooms ?? raw.summary?.bathrooms ?? raw.building?.bathrooms ?? null,
    area:
      raw.squareFeet ??
      raw.sizeInterior ??
      raw.property?.squareFeet ??
      raw.property?.sizeInterior ??
      raw.livingArea ??
      raw.area ??
      null,
    squareFeet:
      raw.squareFeet ??
      raw.sizeInterior ??
      raw.property?.squareFeet ??
      raw.property?.sizeInterior ??
      raw.livingArea ??
      raw.area ??
      null,
    lotSize: raw.lotSize ?? raw.lotSizeArea ?? raw.land?.sizeTotal ?? null,
    lotSizeText: raw.lotSizeText ?? raw.land?.sizeTotalText ?? null,
    yearBuilt:
      raw.yearBuilt ??
      raw.builtYear ??
      raw.constructedDate ??
      raw.property?.builtYear ??
      raw.property?.constructedDate ??
      raw.building?.builtYear ??
      null,
    description:
      raw.description ??
      raw.publicRemarks ??
      raw.remarks ??
      raw.property?.description ??
      raw.property?.remarks ??
      null,
    images: Array.isArray(raw.images)
      ? raw.images
      : Array.isArray(raw.photos)
        ? raw.photos
        : [],
    agents: Array.isArray(raw.agents)
      ? raw.agents
      : Array.isArray(raw.listingAgents)
        ? raw.listingAgents
        : [],
    brokerage: raw.brokerage ?? raw.officeName ?? raw.agency ?? null,
    coordinates:
      raw.coordinates ??
      raw.location?.coordinates ??
      (raw.latitude && raw.longitude ? { lat: raw.latitude, lng: raw.longitude } : null),
    featured: raw.featured ?? raw.isFeatured ?? false,
    openHouse: raw.openHouse ?? raw.hasOpenHouse ?? false,
    listedAt: raw.listedAt ?? raw.listedDate ?? raw.lastUpdated ?? null,
    metrics: buildMetrics(raw),
  };

  return ensurePropertyShape(normalized);
};

const prepareProperties = (entries) => {
  if (!Array.isArray(entries)) {
    return [];
  }

  return entries
    .map((entry) => normalizeProperty(entry))
    .filter((entry) => entry && typeof entry === 'object');
};

const computeStatistics = (properties) => {
  if (!Array.isArray(properties) || properties.length === 0) {
    return { ...defaultStatistics };
  }

  let priceSum = 0;
  let priceCount = 0;
  let domSum = 0;
  let domCount = 0;

  const stats = properties.reduce(
    (acc, property) => {
      acc.total += 1;

      const status = (property.status ?? 'Active').toLowerCase();
      if (status === 'active') {
        acc.active += 1;
      } else if (status === 'pending') {
        acc.pending += 1;
      } else if (status === 'sold') {
        acc.sold += 1;
      }

      if (property.featured) {
        acc.featured += 1;
      }

      if (property.openHouse) {
        acc.openHouses += 1;
      }

      if (typeof property.price === 'number' && !Number.isNaN(property.price)) {
        priceSum += property.price;
        priceCount += 1;
      }

      const dom = toNumber(property.metrics?.daysOnMarket ?? property.daysOnMarket);
      if (dom !== null) {
        domSum += dom;
        domCount += 1;
      }

      return acc;
    },
    { ...defaultStatistics },
  );

  return {
    ...stats,
    averagePrice: priceCount > 0 ? Math.round(priceSum / priceCount) : 0,
    averageDaysOnMarket: domCount > 0 ? Math.round(domSum / domCount) : 0,
  };
};

const matchesText = (haystack, needle) => {
  if (!needle) {
    return true;
  }

  if (!haystack) {
    return false;
  }

  return haystack.toLowerCase().includes(needle.toLowerCase());
};

const buildMarketingCopy = (property) => {
  const locationParts = [property.neighbourhood, property.city, property.province]
    .map((part) => safeString(part))
    .filter(Boolean);
  const locationText = locationParts.length ? ` in ${locationParts.join(', ')}` : '';

  const featureSummary = [
    property.bedrooms ? `${property.bedrooms} bedrooms` : null,
    property.bathrooms ? `${property.bathrooms} bathrooms` : null,
    property.area
      ? `${Number(property.area).toLocaleString(undefined, { maximumFractionDigits: 0 })} sq ft`
      : null,
  ]
    .filter(Boolean)
    .join(' · ');

  let priceText = property.priceFormatted ?? null;
  if (!priceText && typeof property.price === 'number' && !Number.isNaN(property.price)) {
    try {
      priceText = new Intl.NumberFormat('en-CA', {
        style: 'currency',
        currency: 'CAD',
        maximumFractionDigits: 0,
      }).format(property.price);
    } catch (error) {
      priceText = null;
    }
  }

  const highlight = property.highlights?.[0]?.value ?? property.description ?? '';
  const tagLine = (property.tags ?? []).slice(0, 2).join(' • ');

  return `🏡 ${property.title ?? 'Property'}${locationText}. Listed at ${
    priceText ?? 'a competitive price'
  }.${featureSummary ? ` ${featureSummary}.` : ''} ${highlight} ${
    tagLine ? `| ${tagLine}` : ''
  }`.trim();
};

function createPropertyStore() {
  let state = { ...defaultState };
  const listeners = new Set();

  const notify = () => {
    listeners.forEach((listener) => listener());
  };

  const setState = (updater) => {
    const partial = typeof updater === 'function' ? updater(state) : updater;

    if (!partial || typeof partial !== 'object') {
      return;
    }

    state = {
      ...state,
      ...partial,
    };

    notify();
  };

  const getState = () => state;

  const subscribe = (listener) => {
    if (typeof listener !== 'function') {
      return () => {};
    }

    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
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
      const properties = prepareProperties(cached.properties);
      const lastUpdated = cached.lastUpdated ?? null;
      const dataSource = cached.dataSource ?? null;
      const statistics =
        cached.statistics && typeof cached.statistics === 'object'
          ? { ...defaultStatistics, ...cached.statistics }
          : computeStatistics(properties);

      setState({
        properties,
        statistics,
        lastUpdated,
        dataSource,
        isLoading: false,
        loading: false,
      });

      return { properties, statistics, lastUpdated, dataSource };
    } catch (cacheError) {
      console.warn('Failed to load cached property data', cacheError);
      setState({
        isLoading: false,
        loading: false,
        error: 'Failed to load cached property data.',
      });
      return null;
    }
  };

  const fetchProperties = async () => {
    setState({ isLoading: true, loading: true, error: null });

    try {
      const payload = await realtorScrapingService.scrapeWindsorEssexProperties();

      const rawProperties = Array.isArray(payload)
        ? payload
        : Array.isArray(payload?.properties)
          ? payload.properties
          : [];

      const properties = prepareProperties(rawProperties);
      const lastUpdated =
        payload?.lastUpdated ?? rawProperties?.[0]?.lastUpdated ?? new Date().toISOString();
      const statistics = computeStatistics(properties);
      const dataSource = payload?.source ?? null;

      persistToCache({ properties, lastUpdated, statistics, dataSource });

      setState({
        properties,
        statistics,
        lastUpdated,
        dataSource,
        isLoading: false,
        loading: false,
        error: null,
      });

      return properties;
    } catch (fetchError) {
      console.warn('Failed to fetch property data', fetchError);
      const cached = loadFromCache();

      if (cached?.properties?.length) {
        setState({
          isLoading: false,
          loading: false,
          error: 'Unable to refresh properties. Showing the most recent cached results.',
        });

        return cached.properties;
      }

      const responseError = safeString(fetchError?.response?.data?.error);
      const errorMessage =
        responseError || fetchError?.message || 'Failed to fetch property data. Please try again later.';

      setState({
        properties: [],
        statistics: { ...defaultStatistics },
        isLoading: false,
        loading: false,
        lastUpdated: null,
        dataSource: null,
        error: errorMessage,
      });

      return [];
    }
  };

  const refreshProperties = () => fetchProperties();

  const setFilters = (updates) => {
    if (!updates || typeof updates !== 'object') {
      return;
    }

    setState((current) => ({
      filters: {
        ...current.filters,
        ...updates,
      },
    }));
  };

  const toggleStatusFilter = (status) => {
    if (!status) {
      return;
    }

    setState((current) => {
      const nextStatuses = new Set(current.filters.status ?? []);
      const normalizedStatus = `${status}`;

      if (nextStatuses.has(normalizedStatus)) {
        nextStatuses.delete(normalizedStatus);
        if (nextStatuses.size === 0) {
          nextStatuses.add(normalizedStatus);
        }
      } else {
        nextStatuses.add(normalizedStatus);
      }

      return {
        filters: {
          ...current.filters,
          status: Array.from(nextStatuses),
        },
      };
    });
  };

  const setPropertyType = (type) => {
    setState((current) => ({
      filters: {
        ...current.filters,
        propertyType: type,
      },
    }));
  };

  const setPriceSegment = (segment) => {
    setState((current) => ({
      filters: {
        ...current.filters,
        priceSegment: segment,
      },
    }));
  };

  const setSearchTerm = (term) => {
    setState((current) => ({
      filters: {
        ...current.filters,
        searchTerm: term,
        searchQuery: term,
      },
    }));
  };

  const toggleFeaturedOnly = () => {
    setState((current) => ({
      filters: {
        ...current.filters,
        featuredOnly: !current.filters.featuredOnly,
      },
    }));
  };

  const toggleOpenHouseOnly = () => {
    setState((current) => ({
      filters: {
        ...current.filters,
        openHouseOnly: !current.filters.openHouseOnly,
      },
    }));
  };

  const resetFilters = () => {
    setState({
      filters: { ...defaultFilters },
    });
  };

  const clearError = () => {
    setState({ error: null });
  };

  const getFilteredProperties = () => {
    const { properties, filters } = getState();

    if (!Array.isArray(properties)) {
      return [];
    }

    const {
      status,
      propertyType,
      priceSegment,
      featuredOnly,
      openHouseOnly,
      searchTerm,
      searchQuery,
      minPrice,
      maxPrice,
      bedrooms,
      bathrooms,
      propertyTypes,
      municipalities,
    } = filters;

    const textFilter = searchTerm?.trim() || searchQuery?.trim();

    return properties.filter((property) => {
      const listingStatus = property.status ?? 'Active';

      if (Array.isArray(status) && status.length > 0 && !status.includes(listingStatus)) {
        return false;
      }

      const price =
        typeof property.price === 'number' && !Number.isNaN(property.price)
          ? property.price
          : null;

      if (
        typeof minPrice === 'number' &&
        price !== null &&
        !Number.isNaN(minPrice) &&
        price < minPrice
      ) {
        return false;
      }

      if (
        typeof maxPrice === 'number' &&
        price !== null &&
        !Number.isNaN(maxPrice) &&
        price > maxPrice
      ) {
        return false;
      }

      if (typeof bedrooms === 'number') {
        const propertyBedrooms = toNumber(property.bedrooms);
        if (propertyBedrooms !== null && propertyBedrooms < bedrooms) {
          return false;
        }
      }

      if (typeof bathrooms === 'number') {
        const propertyBathrooms = toNumber(property.bathrooms);
        if (propertyBathrooms !== null && propertyBathrooms < bathrooms) {
          return false;
        }
      }

      if (featuredOnly && !property.featured) {
        return false;
      }

      if (openHouseOnly && !property.openHouse) {
        return false;
      }

      if (priceSegment && priceSegment !== 'all') {
        if (price === null) {
          return false;
        }

        if (priceSegment === 'entry' && price >= 500000) {
          return false;
        }

        if (priceSegment === 'move-up' && (price < 500000 || price >= 850000)) {
          return false;
        }

        if (priceSegment === 'luxury' && price < 850000) {
          return false;
        }
      }

      if (propertyType && propertyType !== 'all') {
        const propertyTypeValue = property.propertyType
          ? property.propertyType.toLowerCase()
          : '';

        if (!propertyTypeValue.includes(String(propertyType).toLowerCase())) {
          return false;
        }
      }

      if (Array.isArray(propertyTypes) && propertyTypes.length > 0) {
        const propertyTypeValue = property.propertyType
          ? property.propertyType.toLowerCase()
          : '';

        const matches = propertyTypes.some((candidate) => {
          if (!candidate) {
            return false;
          }

          return propertyTypeValue.includes(String(candidate).toLowerCase());
        });

        if (!matches) {
          return false;
        }
      }

      if (Array.isArray(municipalities) && municipalities.length > 0) {
        const municipality = `${property.municipality ?? property.city ?? ''}`.toLowerCase();
        if (
          municipality &&
          !municipalities.some((candidate) =>
            municipality.includes(String(candidate).toLowerCase()),
          )
        ) {
          return false;
        }
      }

      if (textFilter) {
        const haystack = [
          property.title,
          property.address,
          property.neighbourhood,
          property.city,
          property.description,
        ]
          .map((value) => (value ? String(value) : ''))
          .join(' ');

        if (!matchesText(haystack, textFilter)) {
          return false;
        }
      }

      return true;
    });
  };

  const generatePropertyContent = async (propertyId) => {
    if (!propertyId) {
      return;
    }

    const property = getState().properties.find((item) => item.id === propertyId);

    if (!property) {
      return;
    }

    setState((current) => ({
      generationStatus: {
        ...current.generationStatus,
        [propertyId]: 'loading',
      },
      error: null,
    }));

    try {
      await delay(600);
      const marketingCopy = buildMarketingCopy(property);

      setState((current) => ({
        generationStatus: {
          ...current.generationStatus,
          [propertyId]: 'success',
        },
        generatedContent: {
          ...current.generatedContent,
          [propertyId]: marketingCopy,
        },
      }));

      setTimeout(() => {
        setState((current) => {
          if (current.generationStatus[propertyId] !== 'success') {
            return {};
          }

          const nextStatus = { ...current.generationStatus };
          delete nextStatus[propertyId];

          return {
            generationStatus: nextStatus,
          };
        });
      }, 1600);
    } catch (generationError) {
      console.warn('Failed to generate marketing content', generationError);
      setState((current) => ({
        generationStatus: {
          ...current.generationStatus,
          [propertyId]: 'error',
        },
        error: 'Unable to generate marketing content right now.',
      }));
    }
  };

  return {
    subscribe,
    getState,
    setState,
    fetchProperties,
    refreshProperties,
    loadFromCache,
    setFilters,
    getFilteredProperties,
    clearError,
    toggleStatusFilter,
    setPropertyType,
    setPriceSegment,
    setSearchTerm,
    toggleFeaturedOnly,
    toggleOpenHouseOnly,
    resetFilters,
    generatePropertyContent,
  };
}

const propertyStore = createPropertyStore();

const actions = {
  fetchProperties: propertyStore.fetchProperties,
  refreshProperties: propertyStore.refreshProperties,
  loadFromCache: propertyStore.loadFromCache,
  setFilters: propertyStore.setFilters,
  getFilteredProperties: propertyStore.getFilteredProperties,
  clearError: propertyStore.clearError,
  toggleStatusFilter: propertyStore.toggleStatusFilter,
  setPropertyType: propertyStore.setPropertyType,
  setPriceSegment: propertyStore.setPriceSegment,
  setSearchTerm: propertyStore.setSearchTerm,
  toggleFeaturedOnly: propertyStore.toggleFeaturedOnly,
  toggleOpenHouseOnly: propertyStore.toggleOpenHouseOnly,
  resetFilters: propertyStore.resetFilters,
  generatePropertyContent: propertyStore.generatePropertyContent,
};

propertyStore.setState({ actions });

export function usePropertyStore(selector = (state) => state) {
  return useSyncExternalStore(
    propertyStore.subscribe,
    () => selector(propertyStore.getState()),
    () => selector(propertyStore.getState()),
  );
}

export default usePropertyStore;
