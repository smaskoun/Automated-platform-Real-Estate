import React, { useEffect, useMemo } from 'react';
import {
  AlertCircle,
  Bath,
  Bed,
  Building2,
  CheckCircle2,
  Clock,
  DollarSign,
  Filter,
  MapPin,
  RefreshCcw,
  Ruler,
  Search,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import usePropertyStore from '../stores/propertyStore.js';

const statusFilters = ['Active', 'Pending', 'Sold'];

const statusStyles = {
  Active: {
    badge: 'border-emerald-300 bg-emerald-50/90 text-emerald-700',
    text: 'text-emerald-600',
  },
  Pending: {
    badge: 'border-amber-300 bg-amber-50/90 text-amber-700',
    text: 'text-amber-600',
  },
  Sold: {
    badge: 'border-blue-300 bg-blue-50/90 text-blue-700',
    text: 'text-blue-600',
  },
};

const propertyTypeOptions = [
  { value: 'all', label: 'All property types' },
  { value: 'Single Family', label: 'Single Family' },
  { value: 'Townhome', label: 'Townhome' },
  { value: 'Condo', label: 'Condo' },
];

const priceOptions = [
  { value: 'all', label: 'All price points' },
  { value: 'entry', label: 'Entry (< $500K)' },
  { value: 'move-up', label: 'Move-up ($500K - $850K)' },
  { value: 'luxury', label: 'Luxury (> $850K)' },
];

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
    maximumFractionDigits: 0,
  }).format(value ?? 0);

const formatNumber = (value) => new Intl.NumberFormat('en-CA').format(value ?? 0);

const formatDateTime = (value) => {
  if (!value) return '—';
  try {
    return new Date(value).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  } catch (error) {
    return '—';
  }
};

const formatListedOn = (value) => {
  if (!value) return '—';
  try {
    return new Date(value).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch (error) {
    return '—';
  }
};

const StatCard = ({ icon: Icon, title, value, caption, accent }) => (
  <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="mt-1 text-2xl font-semibold text-gray-900">{value}</p>
      </div>
      <span className={`inline-flex h-11 w-11 items-center justify-center rounded-full border text-base ${accent}`}>
        <Icon className="h-5 w-5" aria-hidden="true" />
      </span>
    </div>
    <p className="mt-4 text-sm text-gray-500">{caption}</p>
  </div>
);

const Metric = ({ label, value }) => (
  <div className="rounded-xl bg-white/60 p-3 text-center shadow-inner">
    <p className="text-lg font-semibold text-gray-900">{formatNumber(value)}</p>
    <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
  </div>
);

const LoadingSkeleton = () => (
  <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
    {Array.from({ length: 3 }).map((_, index) => (
      <div key={index} className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="h-40 w-full animate-pulse rounded-xl bg-gray-200" />
        <div className="mt-4 space-y-3">
          <div className="h-4 w-2/3 animate-pulse rounded bg-gray-200" />
          <div className="h-4 w-1/2 animate-pulse rounded bg-gray-200" />
          <div className="h-3 w-full animate-pulse rounded bg-gray-100" />
          <div className="h-3 w-5/6 animate-pulse rounded bg-gray-100" />
        </div>
      </div>
    ))}
  </div>
);

const EmptyState = ({ onReset }) => (
  <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white p-16 text-center">
    <Building2 className="h-12 w-12 text-gray-300" aria-hidden="true" />
    <h3 className="mt-4 text-lg font-semibold text-gray-900">No properties match your filters</h3>
    <p className="mt-2 max-w-md text-sm text-gray-500">
      Try adjusting the filter settings or reset them to view your complete portfolio of listings.
    </p>
    <div className="mt-6 flex gap-3">
      <button
        type="button"
        onClick={onReset}
        className="inline-flex items-center gap-2 rounded-lg border border-primary-200 bg-primary-50 px-4 py-2 text-sm font-medium text-primary-700 shadow-sm hover:bg-primary-100"
      >
        Reset filters
      </button>
    </div>
  </div>
);

const PropertyCard = ({ property, onGenerateContent, generationState, generatedCopy }) => {
  const styles = statusStyles[property.status] ?? {
    badge: 'border-gray-300 bg-gray-100 text-gray-700',
    text: 'text-gray-600',
  };

  const areaText = typeof property.area === 'number' ? property.area.toLocaleString() : '—';

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
      <div className="relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 p-6 text-white">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-3">
            <span
              className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${styles.badge}`}
            >
              <span className={`h-2.5 w-2.5 rounded-full ${styles.text.replace('text', 'bg')}`} aria-hidden="true" />
              {property.status}
            </span>
            <h3 className="text-2xl font-semibold text-white">{property.title}</h3>
            <p className="flex items-center gap-2 text-sm text-white/80">
              <MapPin className="h-4 w-4" aria-hidden="true" />
              <span>{property.address}</span>
            </p>
            <p className="text-xs uppercase tracking-wide text-white/60">
              Listed {formatListedOn(property.listedAt)} · {property.propertyType}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs uppercase text-white/60">List price</p>
            <p className="text-3xl font-bold">{formatCurrency(property.price)}</p>
            <p className="text-xs text-white/60">Days on market: {property.metrics?.daysOnMarket ?? '—'}</p>
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-6 p-6">
        <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
          <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
            <Bed className="h-4 w-4 text-gray-500" aria-hidden="true" />
            <span className="font-semibold text-gray-900">{property.bedrooms} bd</span>
          </div>
          <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
            <Bath className="h-4 w-4 text-gray-500" aria-hidden="true" />
            <span className="font-semibold text-gray-900">{property.bathrooms} ba</span>
          </div>
          <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
            <Ruler className="h-4 w-4 text-gray-500" aria-hidden="true" />
            <span className="font-semibold text-gray-900">{areaText} sq ft</span>
          </div>
          <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
            <Clock className="h-4 w-4 text-gray-500" aria-hidden="true" />
            <span className="font-semibold text-gray-900">{property.metrics?.daysOnMarket ?? 0} DOM</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {property.tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700"
            >
              {tag}
            </span>
          ))}
        </div>

        <div className="space-y-3 text-sm text-gray-600">
          {property.highlights.map(({ label, value }) => (
            <div key={label} className="flex items-start gap-3 rounded-xl border border-gray-100 bg-gray-50/80 p-3">
              <Sparkles className="mt-0.5 h-4 w-4 text-primary-500" aria-hidden="true" />
              <div>
                <p className="text-sm font-semibold text-gray-900">{label}</p>
                <p className="text-sm text-gray-600">{value}</p>
              </div>
            </div>
          ))}
          <p className="rounded-xl border border-gray-100 bg-white p-3 text-sm text-gray-600 shadow-inner">
            {property.agentNotes}
          </p>
        </div>

        <div className="grid grid-cols-3 gap-3 rounded-2xl border border-gray-100 bg-gray-50 p-3">
          <Metric label="Views" value={property.metrics?.views ?? 0} />
          <Metric label="Saves" value={property.metrics?.saves ?? 0} />
          <Metric label="Inquiries" value={property.metrics?.inquiries ?? 0} />
        </div>

        {generatedCopy ? (
          <div className="space-y-2 rounded-2xl border border-primary-200 bg-primary-50/80 p-4">
            <div className="flex items-center gap-2 text-primary-800">
              <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
              <p className="text-sm font-semibold">Latest marketing copy</p>
            </div>
            <p className="text-sm text-primary-900">{generatedCopy}</p>
          </div>
        ) : null}

        {generationState === 'error' ? (
          <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            <AlertCircle className="h-4 w-4" aria-hidden="true" />
            Something went wrong. Please try again.
          </div>
        ) : null}

        <div className="mt-auto flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => onGenerateContent(property.id)}
            disabled={generationState === 'loading'}
            className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700 disabled:cursor-not-allowed disabled:bg-primary-400"
          >
            <Sparkles className={`h-4 w-4 ${generationState === 'loading' ? 'animate-spin' : ''}`} aria-hidden="true" />
            {generationState === 'loading' ? 'Generating…' : 'Generate marketing copy'}
          </button>
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm transition hover:border-gray-300 hover:bg-gray-50"
          >
            View details
          </button>
        </div>
      </div>
    </article>
  );
};

function PropertiesPage({ user }) {
  const {
    properties,
    filters,
    statistics,
    isLoading,
    error,
    lastUpdated,
    generationStatus,
    generatedContent,
  } = usePropertyStore((state) => ({
    properties: state.properties,
    filters: state.filters,
    statistics: state.statistics,
    isLoading: state.isLoading,
    error: state.error,
    lastUpdated: state.lastUpdated,
    generationStatus: state.generationStatus,
    generatedContent: state.generatedContent,
  }));

  const {
    fetchProperties,
    refreshProperties,
    toggleStatusFilter,
    setPriceSegment,
    setPropertyType,
    setSearchTerm,
    toggleFeaturedOnly,
    toggleOpenHouseOnly,
    generatePropertyContent,
    clearError,
    resetFilters,
  } = usePropertyStore((state) => state.actions);

  useEffect(() => {
    if (!properties.length) {
      fetchProperties();
    }
  }, [fetchProperties, properties.length]);

  const filteredProperties = useMemo(() => {
    return properties.filter((property) => {
      if (filters.status.length && !filters.status.includes(property.status)) {
        return false;
      }

      if (filters.propertyType !== 'all' && property.propertyType !== filters.propertyType) {
        return false;
      }

      if (filters.featuredOnly && !property.featured) {
        return false;
      }

      if (filters.openHouseOnly && !property.openHouse) {
        return false;
      }

      if (filters.priceSegment !== 'all') {
        const price = property.price ?? 0;
        if (filters.priceSegment === 'entry' && price >= 500000) return false;
        if (filters.priceSegment === 'move-up' && (price < 500000 || price >= 850000)) return false;
        if (filters.priceSegment === 'luxury' && price < 850000) return false;
      }

      if (filters.searchTerm) {
        const term = filters.searchTerm.trim().toLowerCase();
        if (term) {
          const haystack = `${property.title} ${property.address} ${property.neighbourhood} ${property.propertyType}`.toLowerCase();
          if (!haystack.includes(term)) {
            return false;
          }
        }
      }

      return true;
    });
  }, [properties, filters]);

  const activeFilterChips = useMemo(() => {
    const chips = [];
    if (filters.propertyType !== 'all') {
      const typeLabel = propertyTypeOptions.find((option) => option.value === filters.propertyType)?.label;
      chips.push(typeLabel ?? filters.propertyType);
    }
    if (filters.priceSegment !== 'all') {
      const priceLabel = priceOptions.find((option) => option.value === filters.priceSegment)?.label;
      chips.push(priceLabel ?? filters.priceSegment);
    }
    if (filters.featuredOnly) {
      chips.push('Featured only');
    }
    if (filters.openHouseOnly) {
      chips.push('Open houses');
    }
    if (filters.searchTerm.trim()) {
      chips.push(`Search: “${filters.searchTerm.trim()}”`);
    }
    if (filters.status.length && filters.status.length !== statusFilters.length) {
      chips.push(`Status: ${filters.status.join(', ')}`);
    }
    return chips;
  }, [filters]);

  const hasActiveFilters = activeFilterChips.length > 0;

  const statCards = [
    {
      icon: Building2,
      title: 'Total listings',
      value: formatNumber(statistics.total),
      caption: `${filteredProperties.length} shown with current filters`,
      accent: 'border-blue-200 bg-blue-50 text-blue-600',
    },
    {
      icon: Sparkles,
      title: 'Active listings',
      value: formatNumber(statistics.active),
      caption: `${statistics.featured} featured · ${statistics.openHouses} with open houses`,
      accent: 'border-emerald-200 bg-emerald-50 text-emerald-600',
    },
    {
      icon: Clock,
      title: 'Avg. days on market',
      value: `${formatNumber(statistics.averageDaysOnMarket)} days`,
      caption: 'Across your current and recently sold listings',
      accent: 'border-amber-200 bg-amber-50 text-amber-600',
    },
    {
      icon: DollarSign,
      title: 'Avg. list price',
      value: formatCurrency(statistics.averagePrice),
      caption: 'Portfolio-wide pricing snapshot',
      accent: 'border-purple-200 bg-purple-50 text-purple-600',
    },
  ];

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-gray-900">Properties</h1>
          <p className="mt-2 max-w-2xl text-sm text-gray-600">
            Manage your active listings, monitor pending deals, and spotlight recently sold successes to fuel your next
            marketing campaign.
          </p>
          {user ? (
            <p className="mt-1 text-xs uppercase tracking-wide text-gray-400">Signed in as {user.username}</p>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={refreshProperties}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm transition hover:border-gray-400 hover:bg-gray-50"
          >
            <RefreshCcw className="h-4 w-4" aria-hidden="true" />
            Refresh listings
          </button>
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700"
          >
            <Sparkles className="h-4 w-4" aria-hidden="true" />
            Quick CMA
          </button>
        </div>
      </header>

      {error ? (
        <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4">
          <AlertCircle className="mt-0.5 h-5 w-5 text-red-600" aria-hidden="true" />
          <div className="space-y-3">
            <div>
              <p className="text-sm font-semibold text-red-700">We couldn’t refresh your portfolio</p>
              <p className="text-sm text-red-600">{error}</p>
            </div>
            <div className="flex flex-wrap gap-3 text-sm">
              <button
                type="button"
                onClick={refreshProperties}
                className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 font-semibold text-white shadow-sm hover:bg-red-700"
              >
                Try again
              </button>
              <button
                type="button"
                onClick={clearError}
                className="inline-flex items-center gap-2 rounded-lg border border-red-200 bg-white px-4 py-2 font-semibold text-red-600 shadow-sm hover:bg-red-50"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      ) : null}

      <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="flex flex-1 flex-col gap-4 md:flex-row">
            <label className="flex-1">
              <span className="sr-only">Search properties</span>
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" aria-hidden="true" />
                <input
                  type="text"
                  value={filters.searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  placeholder="Search by address, neighbourhood, or keywords"
                  className="w-full rounded-lg border border-gray-200 bg-gray-50 pl-10 pr-3 py-2 text-sm text-gray-700 shadow-inner focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
                />
              </div>
            </label>
            <label className="flex-1">
              <span className="sr-only">Filter by property type</span>
              <select
                value={filters.propertyType}
                onChange={(event) => setPropertyType(event.target.value)}
                className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm font-medium text-gray-700 shadow-inner focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
              >
                {propertyTypeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex-1">
              <span className="sr-only">Filter by price segment</span>
              <select
                value={filters.priceSegment}
                onChange={(event) => setPriceSegment(event.target.value)}
                className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm font-medium text-gray-700 shadow-inner focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
              >
                {priceOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={toggleFeaturedOnly}
              className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold shadow-sm transition ${
                filters.featuredOnly
                  ? 'border-primary-300 bg-primary-50 text-primary-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <Sparkles className="h-4 w-4" aria-hidden="true" />
              Featured only
            </button>
            <button
              type="button"
              onClick={toggleOpenHouseOnly}
              className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold shadow-sm transition ${
                filters.openHouseOnly
                  ? 'border-primary-300 bg-primary-50 text-primary-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <Filter className="h-4 w-4" aria-hidden="true" />
              Open houses
            </button>
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-4">
          <div className="flex flex-wrap items-center gap-2">
            {statusFilters.map((status) => {
              const isActive = filters.status.includes(status);
              return (
                <button
                  key={status}
                  type="button"
                  onClick={() => toggleStatusFilter(status)}
                  className={`inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-sm font-medium transition ${
                    isActive
                      ? 'border-primary-400 bg-primary-50 text-primary-700'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <span className={`h-2.5 w-2.5 rounded-full ${statusStyles[status]?.text.replace('text', 'bg') ?? 'bg-gray-300'}`} aria-hidden="true" />
                  {status}
                </button>
              );
            })}
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-gray-500">
            <div className="flex flex-wrap items-center gap-2">
              <TrendingUp className="h-4 w-4 text-gray-400" aria-hidden="true" />
              <span>Showing {filteredProperties.length} of {properties.length} listings</span>
            </div>
            {hasActiveFilters ? (
              <div className="flex flex-wrap items-center gap-2">
                {activeFilterChips.map((chip) => (
                  <span key={chip} className="inline-flex items-center rounded-full border border-primary-200 bg-primary-50 px-3 py-1 text-xs font-medium text-primary-700">
                    {chip}
                  </span>
                ))}
                <button
                  type="button"
                  onClick={resetFilters}
                  className="text-xs font-semibold text-primary-700 underline-offset-4 hover:underline"
                >
                  Clear filters
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
        {statCards.map((card) => (
          <StatCard key={card.title} {...card} />
        ))}
      </section>

      {isLoading ? (
        <LoadingSkeleton />
      ) : filteredProperties.length ? (
        <section className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
          {filteredProperties.map((property) => (
            <PropertyCard
              key={property.id}
              property={property}
              onGenerateContent={generatePropertyContent}
              generationState={generationStatus[property.id]}
              generatedCopy={generatedContent[property.id]}
            />
          ))}
        </section>
      ) : (
        <EmptyState onReset={resetFilters} />
      )}

      <footer className="border-t border-gray-200 pt-6 text-xs text-gray-500">
        <p>
          Portfolio updated {formatDateTime(lastUpdated)} · Data refreshed manually. Use the refresh action to pull the latest
          listing insights from your CRM.
        </p>
      </footer>
    </div>
  );
}

export default PropertiesPage;
