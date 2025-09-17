import { ApifyClient } from 'apify-client';
import puppeteer from 'puppeteer';

const BASE_REALTOR_URL = 'https://www.realtor.ca';

const WINDSOR_ESSEX_START_URLS = [
  'https://www.realtor.ca/on/windsor/real-estate',
  'https://www.realtor.ca/on/tecumseh/real-estate',
  'https://www.realtor.ca/on/lasalle/real-estate',
  'https://www.realtor.ca/on/amherstburg/real-estate',
  'https://www.realtor.ca/on/lakeshore/real-estate',
  'https://www.realtor.ca/on/kingsville/real-estate',
  'https://www.realtor.ca/on/leamington/real-estate',
  'https://www.realtor.ca/on/essex/real-estate',
  'https://www.realtor.ca/on/belle-river/real-estate',
];

const WINDSOR_ESSEX_CITIES = [
  'Windsor',
  'Tecumseh',
  'LaSalle',
  'Amherstburg',
  'Lakeshore',
  'Kingsville',
  'Leamington',
  'Essex',
  'Belle River',
  'Harrow',
  'Maidstone',
  'McGregor',
  'Cottam',
  'Stoney Point',
  'Staples',
].map((city) => city.toLowerCase());

const REALTOR_PAGE_SELECTORS = {
  card: '[data-testid="property-card"]',
  address: '[data-testid="property-card-address"]',
  price: '[data-testid="property-card-price"]',
  bed: '[data-testid="property-card-beds"]',
  bath: '[data-testid="property-card-baths"]',
  sqft: '[data-testid="property-card-sqft"]',
  agentName: '[data-testid="property-card-agent-name"]',
  agentPhone: '[data-testid="property-card-agent-phone"]',
  brokerage: '[data-testid="property-card-agent-brokerage"]',
  image: '[data-testid="property-card-image"] img',
};

const DEFAULT_PUPPETEER_OPTIONS = {
  headless: 'new',
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
};

class RealtorScrapingService {
  constructor() {
    this.apifyClient = new ApifyClient({
      token: process.env?.APIFY_API_KEY || process.env?.VITE_APIFY_API_KEY || '',
    });
  }

  async scrapeWindsorEssexProperties(options = {}) {
    const token = this.apifyClient?.token || this.apifyClient?.options?.token;
    if (!token) {
      console.warn('APIFY_API_KEY is not configured. Falling back to Puppeteer scraping.');
      return this.scrapeWithPuppeteerFallback(options);
    }

    const input = {
      startUrls: WINDSOR_ESSEX_START_URLS.map((url) => ({ url })),
      maxItems: options.maxItems ?? 500,
      proxyConfig: { useApifyProxy: true },
      includeCondos: true,
    };

    let run;
    try {
      run = await this.apifyClient.actor('apify/realtor-ca-scraper').call(input);
    } catch (error) {
      console.error('Apify scraping failed. Falling back to Puppeteer.', error);
      return this.scrapeWithPuppeteerFallback(options);
    }

    if (!run?.defaultDatasetId) {
      console.warn('Apify run completed without a dataset. Falling back to Puppeteer results.');
      return this.scrapeWithPuppeteerFallback(options);
    }

    await this.waitForDatasetReady(run.defaultDatasetId, options.datasetTimeoutMs);

    const datasetClient = this.apifyClient.dataset(run.defaultDatasetId);
    const listings = await this.collectDatasetItems(datasetClient);

    const normalizedListings = listings
      .map((record) => this.normalizeListing(record))
      .filter(Boolean)
      .filter((listing) =>
        listing.city && WINDSOR_ESSEX_CITIES.includes(listing.city.toLowerCase()),
      );

    return this.deduplicateListings(normalizedListings);
  }

  async waitForDatasetReady(datasetId, timeoutMs = 120000) {
    const start = Date.now();
    const pollInterval = 5000;

    while (Date.now() - start < timeoutMs) {
      try {
        const { total, items } = await this.apifyClient
          .dataset(datasetId)
          .listItems({ limit: 1, clean: true });

        if (Number.isInteger(total) && (total > 0 || items.length > 0)) {
          return;
        }
      } catch (error) {
        console.warn('Waiting for dataset readiness failed. Retrying...', error);
      }

      await this.delay(pollInterval);
    }

    console.warn('Timed out waiting for Apify dataset to become ready.');
  }

  async collectDatasetItems(datasetClient, limit = 500) {
    const items = [];
    let offset = 0;

    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { items: pageItems, total } = await datasetClient.listItems({
        clean: true,
        offset,
        limit,
      });

      if (!pageItems?.length) {
        break;
      }

      items.push(...pageItems);
      offset += pageItems.length;

      if (typeof total === 'number' && offset >= total) {
        break;
      }
    }

    return items;
  }

  normalizeListing(raw) {
    if (!raw || typeof raw !== 'object') {
      return null;
    }

    const location =
      raw.location ||
      raw.address ||
      raw.property?.address ||
      raw.property?.location ||
      raw.propertyLocation ||
      {};

    const city = this.cleanString(
      location.city || location.municipality || raw.city || raw.municipality,
    );
    const province = this.cleanString(location.province || location.state || 'ON');
    const postalCode = this.cleanString(location.postalCode || location.postal_code);
    const price = this.parsePrice(
      raw.price || raw.priceValue || raw.property?.price || raw.property?.priceValue,
    );
    const priceFormatted =
      price !== null
        ? this.formatPrice(price)
        : this.cleanString(raw.displayPrice || raw.priceFormatted || raw.priceLabel);

    const features = this.extractFeatures(raw);
    const images = this.extractImages(raw);
    const agents = this.extractAgents(raw);
    const coordinates = this.extractCoordinates(raw);

    const listing = {
      id:
        raw.id ||
        raw.listingId ||
        raw.mlsId ||
        raw.mlsNumber ||
        raw.property?.mlsNumber ||
        raw.property?.id ||
        null,
      mlsNumber: this.cleanString(
        raw.mlsNumber ||
          raw.mlsId ||
          raw.property?.mlsNumber ||
          raw.property?.mlsId ||
          raw.listingId,
      ),
      address: this.formatAddress(location, raw),
      city,
      province,
      postalCode,
      country: this.cleanString(location.country || 'Canada'),
      price,
      priceFormatted,
      priceText: this.cleanString(raw.price || raw.priceLabel || raw.displayPrice),
      propertyType:
        this.cleanString(
          raw.propertyType || raw.type || raw.property?.type || raw.category || raw.building?.type,
        ) || null,
      description: this.cleanString(
        raw.description ||
          raw.publicRemarks ||
          raw.remarks ||
          raw.property?.description ||
          raw.property?.remarks,
      ),
      bedrooms: features.bedrooms,
      bathrooms: features.bathrooms,
      squareFeet: features.squareFeet,
      lotSize: features.lotSize,
      lotSizeText: features.lotSizeText,
      yearBuilt: features.yearBuilt,
      listingUrl: this.ensureAbsoluteUrl(
        raw.url || raw.detailUrl || raw.detailPageUrl || raw.permalink || raw.property?.url,
      ),
      images,
      agents,
      brokerage: this.cleanString(
        raw.brokerage || raw.officeName || raw.office || raw.broker || raw.agency,
      ),
      coordinates,
      lastUpdated: raw.lastUpdated || raw.updated || raw.lastUpdatedAt || null,
    };

    return listing;
  }

  formatAddress(location = {}, raw = {}) {
    if (raw.addressText) {
      return this.cleanString(raw.addressText);
    }

    const parts = [
      location.addressLine1 || location.address1 || location.streetAddress || location.line1,
      location.addressLine2 || location.address2 || location.streetAddress2 || location.line2,
      location.city || location.municipality,
      location.province || location.state,
      location.postalCode || location.postal_code,
    ]
      .map((part) => this.cleanString(part))
      .filter(Boolean);

    return parts.join(', ') || null;
  }

  parsePrice(value) {
    if (value === null || value === undefined) {
      return null;
    }

    if (typeof value === 'number' && !Number.isNaN(value)) {
      return value;
    }

    if (typeof value === 'object') {
      const amount = value.amount || value.value || value.price;
      if (amount !== undefined) {
        return this.parsePrice(amount);
      }
    }

    if (typeof value === 'string') {
      const normalized = value.replace(/[^0-9.,-]+/g, '');
      const match = normalized.match(/-?\d+(?:[.,]\d+)?/);
      if (match) {
        const numericValue = Number(match[0].replace(/,/g, ''));
        if (!Number.isNaN(numericValue)) {
          return numericValue;
        }
      }
    }

    return null;
  }

  formatPrice(value) {
    if (value === null || value === undefined || Number.isNaN(value)) {
      return null;
    }

    try {
      return new Intl.NumberFormat('en-CA', {
        style: 'currency',
        currency: 'CAD',
        maximumFractionDigits: 0,
      }).format(value);
    } catch (error) {
      console.warn('Failed to format price', value, error);
      return value?.toString?.() ?? null;
    }
  }

  extractFeatures(listing) {
    const normalizedDetails = this.normalizeDetails(listing);
    const getDetailValue = (...keywords) => {
      const keywordSet = keywords.map((keyword) => keyword.toLowerCase());
      const detail = normalizedDetails.find((entry) =>
        keywordSet.some((keyword) => entry.label?.toLowerCase().includes(keyword)),
      );
      return detail?.value ?? detail?.text ?? null;
    };

    const bedrooms =
      this.extractNumber(
        this.valueFromPaths(listing, [
          'bedrooms',
          'bedroomsTotal',
          'bedroomsAboveGround',
          'property.bedrooms',
          'property.building.bedrooms',
          'building.bedrooms',
          'building.bedroomsTotal',
          'summary.bedrooms',
        ]),
      ) || this.extractNumber(getDetailValue('bedroom', 'bed'));

    const bathrooms =
      this.extractNumber(
        this.valueFromPaths(listing, [
          'bathrooms',
          'bathroomsTotal',
          'property.bathrooms',
          'property.building.bathrooms',
          'building.bathrooms',
          'summary.bathrooms',
        ]),
      ) || this.extractNumber(getDetailValue('bathroom', 'bath'));

    const squareFeet =
      this.extractNumber(
        this.valueFromPaths(listing, [
          'sizeInterior',
          'building.sizeInterior',
          'building.totalFinishedArea',
          'property.building.sizeInterior',
          'property.squareFeet',
          'squareFootage',
          'area',
        ]),
      ) || this.extractNumber(getDetailValue('square feet', 'sqft', 'interior'));

    const lotSizeRaw =
      this.valueFromPaths(listing, [
        'land.sizeTotal',
        'land.sizeTotalText',
        'land.sizeFrontage',
        'property.land.sizeTotal',
        'lotSize',
        'lotSizeArea',
        'property.landSize',
      ]) || getDetailValue('lot size', 'size total', 'land size');

    const yearBuilt =
      this.extractNumber(
        this.valueFromPaths(listing, [
          'building.builtYear',
          'building.constructedDate',
          'property.building.builtYear',
          'property.building.constructedDate',
        ]),
      ) || this.extractNumber(getDetailValue('built', 'constructed', 'year'));

    return {
      bedrooms: bedrooms ?? null,
      bathrooms: bathrooms ?? null,
      squareFeet: squareFeet ?? null,
      lotSize: this.extractNumber(lotSizeRaw),
      lotSizeText: this.cleanString(lotSizeRaw),
      yearBuilt: yearBuilt ?? null,
    };
  }

  normalizeDetails(listing) {
    const candidates = [];
    if (Array.isArray(listing.details)) candidates.push(listing.details);
    if (Array.isArray(listing.property?.details)) candidates.push(listing.property.details);
    if (Array.isArray(listing.propertyDetails)) candidates.push(listing.propertyDetails);
    if (Array.isArray(listing.building?.details)) candidates.push(listing.building.details);

    return candidates
      .flat()
      .map((detail) => {
        if (!detail) {
          return null;
        }

        if (typeof detail === 'string') {
          return { label: detail, value: detail };
        }

        if (detail.label || detail.name) {
          return {
            label: detail.label || detail.name || null,
            value: detail.value ?? detail.text ?? detail.display ?? null,
          };
        }

        if (Array.isArray(detail) && detail.length >= 2) {
          return { label: detail[0], value: detail[1] };
        }

        return null;
      })
      .filter(Boolean);
  }

  valueFromPaths(object, paths) {
    for (const path of paths) {
      const segments = path.split('.');
      let current = object;
      let valid = true;

      for (const segment of segments) {
        if (current && Object.prototype.hasOwnProperty.call(current, segment)) {
          current = current[segment];
        } else {
          valid = false;
          break;
        }
      }

      if (valid && current !== undefined && current !== null && current !== '') {
        return current;
      }
    }

    return null;
  }

  extractNumber(value) {
    if (value === null || value === undefined) {
      return null;
    }

    if (typeof value === 'number') {
      return Number.isNaN(value) ? null : value;
    }

    if (typeof value === 'string') {
      const normalized = value.replace(/[^0-9.,-]+/g, '');
      const match = normalized.match(/-?\d+(?:[.,]\d+)?/);
      if (match) {
        const numberValue = Number(match[0].replace(/,/g, ''));
        return Number.isNaN(numberValue) ? null : numberValue;
      }
    }

    return null;
  }

  extractImages(listing) {
    const imageSet = new Set();
    const addImage = (url) => {
      if (!url || typeof url !== 'string') return;
      const trimmed = url.trim();
      if (!trimmed) return;

      if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
        imageSet.add(trimmed);
      } else {
        imageSet.add(`${BASE_REALTOR_URL}${trimmed.startsWith('/') ? '' : '/'}${trimmed}`);
      }
    };

    const candidateArrays = [
      listing.images,
      listing.photos,
      listing.media,
      listing.gallery,
      listing.property?.photos,
      listing.property?.images,
      listing.property?.media,
      listing.property?.photo?.highResPaths,
      listing.property?.photo?.lowResPaths,
      listing.property?.photo?.url,
    ];

    for (const candidate of candidateArrays) {
      if (typeof candidate === 'string') {
        addImage(candidate);
      } else if (Array.isArray(candidate)) {
        candidate.forEach(addImage);
      } else if (candidate && typeof candidate === 'object') {
        Object.values(candidate).forEach(addImage);
      }
    }

    return Array.from(imageSet);
  }

  extractAgents(listing) {
    const agents = [];

    const pushAgent = (agent) => {
      if (!agent) {
        return;
      }

      const name = this.cleanString(
        agent.name || agent.fullName || agent.agentName || agent.agent || agent.contactName,
      );
      const phone = this.cleanString(
        agent.phone || agent.telephone || agent.phoneNumber || agent.contactPhone,
      );
      const email = this.cleanString(agent.email || agent.contactEmail);
      const brokerage = this.cleanString(
        agent.brokerage || agent.office || agent.officeName || agent.company || agent.broker,
      );
      const title = this.cleanString(agent.title || agent.position || agent.role);

      if (name || phone || email || brokerage) {
        agents.push({ name, phone, email, brokerage, title });
      }
    };

    const candidateCollections = [
      listing.agents,
      listing.agent,
      listing.property?.agents,
      listing.property?.agent,
      listing.property?.representatives,
      listing.contact,
      listing.representatives,
      listing.brokerage?.agents,
      listing.office?.agents,
    ];

    for (const collection of candidateCollections) {
      if (Array.isArray(collection)) {
        collection.forEach(pushAgent);
      } else if (collection && typeof collection === 'object') {
        pushAgent(collection);
      }
    }

    if (!agents.length) {
      const fallbackBrokerage = this.cleanString(
        listing.brokerage || listing.office || listing.officeName || listing.company,
      );
      if (fallbackBrokerage) {
        agents.push({ name: null, phone: null, email: null, brokerage: fallbackBrokerage, title: null });
      }
    }

    return this.deduplicateAgents(agents);
  }

  deduplicateAgents(agents) {
    const unique = new Map();

    for (const agent of agents) {
      const key = (agent.name || agent.email || agent.phone || agent.brokerage || '').toLowerCase();
      if (!unique.has(key)) {
        unique.set(key, agent);
      }
    }

    return Array.from(unique.values());
  }

  extractCoordinates(listing) {
    const lat = this.extractNumber(
      this.valueFromPaths(listing, [
        'coordinates.lat',
        'coordinates.latitude',
        'location.lat',
        'location.latitude',
        'property.location.lat',
        'property.location.latitude',
        'geo.lat',
        'geo.latitude',
      ]),
    );

    const lng = this.extractNumber(
      this.valueFromPaths(listing, [
        'coordinates.lng',
        'coordinates.lon',
        'coordinates.longitude',
        'location.lng',
        'location.lon',
        'location.longitude',
        'property.location.lng',
        'property.location.lon',
        'property.location.longitude',
        'geo.lng',
        'geo.lon',
        'geo.longitude',
      ]),
    );

    if (lat !== null && lng !== null) {
      return { lat, lng };
    }

    return null;
  }

  ensureAbsoluteUrl(url) {
    if (!url || typeof url !== 'string') {
      return null;
    }

    if (/^https?:\/\//i.test(url)) {
      return url;
    }

    return `${BASE_REALTOR_URL}${url.startsWith('/') ? '' : '/'}${url}`;
  }

  cleanString(value) {
    if (typeof value !== 'string') {
      return value ?? null;
    }

    const trimmed = value.trim();
    return trimmed.length ? trimmed : null;
  }

  async scrapeWithPuppeteerFallback(options = {}) {
    const { fallbackUrls = WINDSOR_ESSEX_START_URLS, ...fallbackOptions } = options;
    const results = [];

    for (const url of fallbackUrls) {
      try {
        const listings = await this.customScrapeRealtor(url, fallbackOptions);
        if (Array.isArray(listings)) {
          results.push(...listings);
        } else if (listings) {
          results.push(listings);
        }
      } catch (error) {
        console.warn(`Failed Puppeteer scrape for ${url}`, error);
      }
    }

    return this.deduplicateListings(results).filter(
      (listing) => listing.city && WINDSOR_ESSEX_CITIES.includes(listing.city.toLowerCase()),
    );
  }

  async customScrapeRealtor(url, options = {}) {
    const launchOptions = { ...DEFAULT_PUPPETEER_OPTIONS, ...(options.launchOptions || {}) };
    const timeout = options.timeout ?? 60000;
    const selectors = { ...REALTOR_PAGE_SELECTORS, ...(options.selectors || {}) };
    const limit = options.limit ?? 24;

    const browser = await puppeteer.launch(launchOptions);
    try {
      const page = await browser.newPage();
      await page.goto(url, { waitUntil: 'networkidle2', timeout });
      await page.waitForSelector(selectors.address, { timeout }).catch(() => null);

      const scrapedListings = await page.evaluate(
        (sel, max, baseUrl) => {
          const cards = sel.card
            ? Array.from(document.querySelectorAll(sel.card))
            : Array.from(document.querySelectorAll(sel.address)).map((node) => node.closest('article'));

          return cards.slice(0, max).map((card) => {
            const getText = (selector) => {
              if (!selector) return null;
              const element = card.querySelector(selector);
              return element ? element.textContent.trim() : null;
            };

            const getImageSrc = (selector) => {
              if (!selector) return null;
              const element = card.querySelector(selector);
              if (!element) return null;
              return element.getAttribute('data-src') || element.getAttribute('src');
            };

            const linkElement = card.querySelector('a[href]');
            const href = linkElement?.getAttribute('href') || null;

            return {
              address: getText(sel.address),
              priceText: getText(sel.price),
              bedsText: getText(sel.bed),
              bathsText: getText(sel.bath),
              sqftText: getText(sel.sqft),
              agentName: getText(sel.agentName),
              agentPhone: getText(sel.agentPhone),
              brokerage: getText(sel.brokerage),
              image: getImageSrc(sel.image),
              listingUrl: href ? (href.startsWith('http') ? href : `${baseUrl}${href}`) : null,
            };
          });
        },
        selectors,
        limit,
        BASE_REALTOR_URL,
      );

      return scrapedListings
        .map((item) => this.normalizeFallbackListing(item))
        .filter(Boolean);
    } finally {
      await browser.close();
    }
  }

  normalizeFallbackListing(item) {
    if (!item || !item.address) {
      return null;
    }

    const priceValue = this.parsePrice(item.priceText);
    const city = this.extractCityFromAddress(item.address);

    return {
      id: null,
      mlsNumber: null,
      address: this.cleanString(item.address),
      city,
      province: 'ON',
      postalCode: null,
      country: 'Canada',
      price: priceValue,
      priceFormatted: priceValue !== null ? this.formatPrice(priceValue) : item.priceText,
      priceText: item.priceText,
      propertyType: null,
      description: null,
      bedrooms: this.extractNumber(item.bedsText),
      bathrooms: this.extractNumber(item.bathsText),
      squareFeet: this.extractNumber(item.sqftText),
      lotSize: null,
      lotSizeText: null,
      yearBuilt: null,
      listingUrl: this.ensureAbsoluteUrl(item.listingUrl),
      images: item.image ? [this.ensureAbsoluteUrl(item.image)] : [],
      agents: this.normalizeFallbackAgents(item),
      brokerage: this.cleanString(item.brokerage),
      coordinates: null,
      lastUpdated: null,
    };
  }

  normalizeFallbackAgents(item) {
    const agentName = this.cleanString(item.agentName);
    const agentPhone = this.cleanString(item.agentPhone);
    const brokerage = this.cleanString(item.brokerage);

    if (!agentName && !agentPhone && !brokerage) {
      return [];
    }

    return [
      {
        name: agentName,
        phone: agentPhone,
        email: null,
        brokerage,
        title: null,
      },
    ];
  }

  extractCityFromAddress(address) {
    if (!address || typeof address !== 'string') {
      return null;
    }

    const parts = address
      .split(',')
      .map((part) => part.trim())
      .filter(Boolean);

    for (const part of parts) {
      if (WINDSOR_ESSEX_CITIES.includes(part.toLowerCase())) {
        return part;
      }
    }

    if (parts.length >= 2) {
      return parts[parts.length - 2];
    }

    return parts[0] ?? null;
  }

  deduplicateListings(listings) {
    const unique = new Map();

    for (const listing of listings) {
      if (!listing) continue;

      const key =
        (listing.mlsNumber && listing.mlsNumber.toLowerCase()) ||
        (listing.listingUrl && listing.listingUrl.toLowerCase()) ||
        (listing.address && listing.address.toLowerCase());

      if (!key) {
        continue;
      }

      if (!unique.has(key)) {
        unique.set(key, listing);
      }
    }

    return Array.from(unique.values());
  }

  delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

const realtorScrapingService = new RealtorScrapingService();

export default realtorScrapingService;
export { RealtorScrapingService, WINDSOR_ESSEX_START_URLS, WINDSOR_ESSEX_CITIES };
