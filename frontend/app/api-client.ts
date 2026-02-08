import axios from 'axios';
import { API_BASE_URL, AI_AGENT_API_BASE_URL } from './api.config';

// Create axios instances for different APIs
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

const aiAgentClient = axios.create({
  baseURL: AI_AGENT_API_BASE_URL,
});

// Request interceptor to add authorization token
const addAuthHeader = (config: any) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

// Add interceptors to both clients
apiClient.interceptors.request.use(addAuthHeader);
aiAgentClient.interceptors.request.use(addAuthHeader);

// Response interceptor to handle unauthorized responses
const handleUnauthorized = (error: any) => {
  if (error.response?.status === 401 || error.response?.status === 403) {
    // Remove token and redirect to login
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      // Optionally redirect to login page - this would need to be handled by the calling component
    }
  }
  return Promise.reject(error);
};

apiClient.interceptors.response.use(
  (response) => response,
  handleUnauthorized
);

aiAgentClient.interceptors.response.use(
  (response) => response,
  handleUnauthorized
);

export { apiClient, aiAgentClient };