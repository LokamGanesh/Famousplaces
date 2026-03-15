import axios from 'axios';

// Replace with your actual Google Cloud Run API URL
// Example: https://tourism-api-abc123-uc.a.run.app
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchRecommendations = async (city) => {
  try {
    const response = await api.get(`/recommend/${encodeURIComponent(city)}`);
    return response.data;
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data.detail || 'Failed to fetch recommendations');
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error('Error making request: ' + error.message);
    }
  }
};

export const fetchCities = async () => {
  try {
    const response = await api.get('/cities');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch cities:', error);
    return { cities: [], count: 0 };
  }
};

export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    return { status: 'unhealthy', model_loaded: false, dataset_size: 0 };
  }
};

export default api;
