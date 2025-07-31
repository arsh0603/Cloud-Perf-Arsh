// API configuration and utility functions
const API_BASE_URL = 'http://localhost:8000/api';

// API endpoints
export const API_ENDPOINTS = {
  fetchDetails: `${API_BASE_URL}/fetch-details/`,
  fetchGraphData: `${API_BASE_URL}/fetch-graph-data/`,
  cacheManagement: `${API_BASE_URL}/cache-management/`,
  fetchMultipleRuns: `${API_BASE_URL}/fetch-multiple-runs/`,
};

// Generic API request handler
const apiRequest = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// Specific API functions
export const apiService = {
  // Fetch data for single ID
  fetchSingleDetails: async (id) => {
    const url = `${API_ENDPOINTS.fetchDetails}?id=${id}`;
    return apiRequest(url);
  },

  // Fetch data for comparison (two IDs)
  fetchComparisonDetails: async (id1, id2) => {
    const url = `${API_ENDPOINTS.fetchDetails}?id1=${id1}&id2=${id2}`;
    return apiRequest(url);
  },

  // Fetch graph data for single ID
  fetchGraphData: async (runId) => {
    const url = `${API_ENDPOINTS.fetchGraphData}?run_id1=${runId}`;
    return apiRequest(url);
  },

  // Fetch graph data for comparison
  fetchGraphDataComparison: async (runId1, runId2) => {
    const url = `${API_ENDPOINTS.fetchGraphData}?run_id1=${runId1}&run_id2=${runId2}`;
    return apiRequest(url);
  },

  // Fetch cache status
  fetchCacheStatus: async () => {
    return apiRequest(API_ENDPOINTS.cacheManagement);
  },

  // Clear cache
  clearCache: async () => {
    return apiRequest(API_ENDPOINTS.cacheManagement, {
      method: 'DELETE',
    });
  },

  // Fetch multiple runs data
  fetchMultipleRuns: async (ids) => {
    const idsParam = Array.isArray(ids) ? ids.join(',') : ids;
    const url = `${API_ENDPOINTS.fetchMultipleRuns}?ids=${idsParam}`;
    return apiRequest(url);
  },
};

export default apiService;
