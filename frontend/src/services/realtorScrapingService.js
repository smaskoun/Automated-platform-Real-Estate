import api from '../api.js';

const realtorScrapingService = {
  async scrapeWindsorEssexProperties(params = {}) {
    const response = await api.get('/realtor/properties', { params });
    return response?.data ?? { properties: [] };
  },
};

export default realtorScrapingService;
