import { useSyncExternalStore } from 'react';

const mockProperties = [
  {
    id: 'WIN-4801',
    title: 'Riverside Executive Home',
    status: 'Active',
    price: 849000,
    address: '125 Riverfront Ave, Windsor, ON',
    neighbourhood: 'Riverside',
    propertyType: 'Single Family',
    bedrooms: 4,
    bathrooms: 3.5,
    area: 3100,
    tags: ['Waterfront', 'Smart Home', 'Three-Car Garage'],
    highlights: [
      { label: 'Key Feature', value: 'Panoramic Detroit River views from every level' },
      { label: 'Updates', value: 'Complete 2023 renovation with designer finishes' },
    ],
    agentNotes:
      'Open-concept living with covered outdoor lounge and private dock—perfect for executive entertaining.',
    metrics: { daysOnMarket: 12, views: 982, saves: 34, inquiries: 18 },
    featured: true,
    openHouse: true,
    listedAt: '2024-06-24',
  },
  {
    id: 'WIN-4824',
    title: 'Walkerville Heritage Charmer',
    status: 'Pending',
    price: 629000,
    address: '412 Devonshire Rd, Windsor, ON',
    neighbourhood: 'Walkerville',
    propertyType: 'Townhome',
    bedrooms: 3,
    bathrooms: 2.5,
    area: 2100,
    tags: ['Heritage District', 'Private Courtyard'],
    highlights: [
      { label: 'Lifestyle', value: 'Steps from boutique cafes, galleries, and riverfront trail' },
      { label: 'Seller Notes', value: 'Meticulously maintained with preserved century details' },
    ],
    agentNotes:
      'Buyers loved the blend of original character and modern comforts—status conditional on financing.',
    metrics: { daysOnMarket: 9, views: 756, saves: 21, inquiries: 11 },
    featured: false,
    openHouse: false,
    listedAt: '2024-06-30',
  },
  {
    id: 'WIN-4788',
    title: 'South Windsor Family Retreat',
    status: 'Active',
    price: 719900,
    address: '87 Maiden Lane W, Windsor, ON',
    neighbourhood: 'South Windsor',
    propertyType: 'Single Family',
    bedrooms: 4,
    bathrooms: 3,
    area: 2650,
    tags: ['Family Friendly Street', 'Finished Lower Level'],
    highlights: [
      { label: 'Upgrades', value: 'Custom kitchen with quartz waterfall island and walk-in pantry' },
      { label: 'Outdoor Living', value: 'Fully landscaped backyard with covered deck and gas firepit' },
    ],
    agentNotes:
      'Zoned for top-rated schools with a flexible in-law suite—ideal for multigenerational living.',
    metrics: { daysOnMarket: 5, views: 548, saves: 19, inquiries: 14 },
    featured: true,
    openHouse: true,
    listedAt: '2024-07-02',
  },
  {
    id: 'WIN-4705',
    title: 'Downtown Penthouse Loft',
    status: 'Sold',
    price: 915000,
    address: '180 University Ave W PH1203, Windsor, ON',
    neighbourhood: 'Downtown',
    propertyType: 'Condo',
    bedrooms: 2,
    bathrooms: 2,
    area: 1850,
    tags: ['City Skyline Views', 'Private Rooftop Terrace'],
    highlights: [
      { label: 'Buyer Profile', value: 'Downsizers relocating from Toronto seeking turnkey luxury' },
      { label: 'Closing', value: 'Firm sale over ask with quick 21-day closing' },
    ],
    agentNotes:
      'Record-setting condo sale for the building—keep note for your next listing presentation.',
    metrics: { daysOnMarket: 6, views: 1102, saves: 42, inquiries: 27 },
    featured: false,
    openHouse: false,
    listedAt: '2024-05-18',
  },
];

const defaultFilters = {
  status: ['Active', 'Pending', 'Sold'],
  propertyType: 'all',
  priceSegment: 'all',
  featuredOnly: false,
  openHouseOnly: false,
  searchTerm: '',
};

const initialState = {
  properties: [],
  filters: { ...defaultFilters },
  statistics: {
    total: 0,
    active: 0,
    pending: 0,
    sold: 0,
    featured: 0,
    openHouses: 0,
    averagePrice: 0,
    averageDaysOnMarket: 0,
  },
  generatedContent: {},
  generationStatus: {},
  isLoading: false,
  error: null,
  lastUpdated: null,
};

const propertyStore = {
  state: initialState,
  listeners: new Set(),
  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  },
  setState(updater) {
    const previous = this.state;
    const partial = typeof updater === 'function' ? updater(previous) : updater;
    this.state = {
      ...previous,
      ...partial,
      actions: this.state.actions,
    };
    this.listeners.forEach((listener) => listener());
  },
};

const simulateNetwork = (value, delay = 600) =>
  new Promise((resolve) => {
    setTimeout(() => resolve(value), delay);
  });

const formatCurrency = (value) => {
  if (!value) {
    return '$0';
  }
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
    maximumFractionDigits: 0,
  }).format(value);
};

const buildMarketingCopy = (property) => {
  const featureSummary = [
    `${property.bedrooms} bedrooms`,
    `${property.bathrooms} bathrooms`,
    `${property.area.toLocaleString()} sq ft`,
  ]
    .filter(Boolean)
    .join(' · ');

  const highlight = property.highlights?.[0]?.value ?? '';
  const tagLine = property.tags.slice(0, 2).join(' • ');

  return `🏡 ${property.title} in ${property.neighbourhood}. Listed at ${formatCurrency(
    property.price,
  )}. ${featureSummary}. ${highlight} ${tagLine ? `| ${tagLine}` : ''}`.trim();
};

const computeStatistics = (properties) => {
  if (!properties.length) {
    return {
      total: 0,
      active: 0,
      pending: 0,
      sold: 0,
      featured: 0,
      openHouses: 0,
      averagePrice: 0,
      averageDaysOnMarket: 0,
    };
  }

  const totals = properties.reduce(
    (acc, property) => {
      acc.total += 1;
      acc.averagePrice += property.price;
      acc.averageDaysOnMarket += property.metrics?.daysOnMarket ?? 0;
      if (property.status === 'Active') acc.active += 1;
      if (property.status === 'Pending') acc.pending += 1;
      if (property.status === 'Sold') acc.sold += 1;
      if (property.featured) acc.featured += 1;
      if (property.openHouse) acc.openHouses += 1;
      return acc;
    },
    {
      total: 0,
      active: 0,
      pending: 0,
      sold: 0,
      featured: 0,
      openHouses: 0,
      averagePrice: 0,
      averageDaysOnMarket: 0,
    },
  );

  return {
    total: totals.total,
    active: totals.active,
    pending: totals.pending,
    sold: totals.sold,
    featured: totals.featured,
    openHouses: totals.openHouses,
    averagePrice: Math.round(totals.averagePrice / totals.total),
    averageDaysOnMarket: Math.round(totals.averageDaysOnMarket / totals.total),
  };
};

const actions = {};

actions.fetchProperties = async () => {
  propertyStore.setState({ isLoading: true, error: null });

  try {
    const listings = await simulateNetwork(mockProperties);
    propertyStore.setState({
      properties: listings,
      statistics: computeStatistics(listings),
      isLoading: false,
      lastUpdated: new Date().toISOString(),
    });
  } catch (error) {
    propertyStore.setState({
      error: 'Unable to load properties. Please try again.',
      isLoading: false,
    });
  }
};

actions.refreshProperties = async () => {
  await actions.fetchProperties();
};

actions.toggleStatusFilter = (status) => {
  propertyStore.setState((state) => {
    const activeStatuses = new Set(state.filters.status);

    if (activeStatuses.has(status)) {
      activeStatuses.delete(status);
      if (activeStatuses.size === 0) {
        activeStatuses.add(status);
      }
    } else {
      activeStatuses.add(status);
    }

    return {
      filters: {
        ...state.filters,
        status: Array.from(activeStatuses),
      },
    };
  });
};

actions.setPropertyType = (type) => {
  propertyStore.setState((state) => ({
    filters: {
      ...state.filters,
      propertyType: type,
    },
  }));
};

actions.setPriceSegment = (segment) => {
  propertyStore.setState((state) => ({
    filters: {
      ...state.filters,
      priceSegment: segment,
    },
  }));
};

actions.setSearchTerm = (term) => {
  propertyStore.setState((state) => ({
    filters: {
      ...state.filters,
      searchTerm: term,
    },
  }));
};

actions.toggleFeaturedOnly = () => {
  propertyStore.setState((state) => ({
    filters: {
      ...state.filters,
      featuredOnly: !state.filters.featuredOnly,
    },
  }));
};

actions.toggleOpenHouseOnly = () => {
  propertyStore.setState((state) => ({
    filters: {
      ...state.filters,
      openHouseOnly: !state.filters.openHouseOnly,
    },
  }));
};

actions.resetFilters = () => {
  propertyStore.setState({
    filters: { ...defaultFilters },
  });
};

actions.clearError = () => {
  propertyStore.setState({ error: null });
};

actions.generatePropertyContent = async (propertyId) => {
  const property = propertyStore.state.properties.find((item) => item.id === propertyId);

  if (!property) {
    return;
  }

  propertyStore.setState((state) => ({
    generationStatus: {
      ...state.generationStatus,
      [propertyId]: 'loading',
    },
    error: null,
  }));

  try {
    const marketingCopy = await simulateNetwork(buildMarketingCopy(property), 700);
    propertyStore.setState((state) => ({
      generationStatus: {
        ...state.generationStatus,
        [propertyId]: 'success',
      },
      generatedContent: {
        ...state.generatedContent,
        [propertyId]: marketingCopy,
      },
    }));

    setTimeout(() => {
      propertyStore.setState((state) => {
        if (state.generationStatus[propertyId] !== 'success') {
          return {};
        }

        const nextStatus = { ...state.generationStatus };
        delete nextStatus[propertyId];

        return {
          generationStatus: nextStatus,
        };
      });
    }, 1600);
  } catch (error) {
    propertyStore.setState((state) => ({
      generationStatus: {
        ...state.generationStatus,
        [propertyId]: 'error',
      },
      error: 'Unable to generate marketing content right now.',
    }));
  }
};

propertyStore.state = {
  ...propertyStore.state,
  actions,
};

export function usePropertyStore(selector = (state) => state) {
  return useSyncExternalStore(
    propertyStore.subscribe.bind(propertyStore),
    () => selector(propertyStore.state),
    () => selector(propertyStore.state),
  );
}

export default usePropertyStore;
