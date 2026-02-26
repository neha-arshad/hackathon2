import axios from 'axios';
import { API_BASE_URL, AI_AGENT_API_BASE_URL } from './api.config';

// Create axios instances for different APIs
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

const aiAgentClient = axios.create({
  baseURL: AI_AGENT_API_BASE_URL,
});

/**
 * Clean a token by removing any "Bearer " prefix and trimming whitespace.
 * This ensures the token stored/used is always the raw JWT without prefixes.
 */
export function cleanToken(token: string | null): string | null {
  if (!token) return null;

  let cleaned = token.trim();

  // Keep removing "Bearer " prefix until none remains (handles "Bearer Bearer ..." edge case)
  while (/^Bearer\s+/i.test(cleaned)) {
    cleaned = cleaned.replace(/^Bearer\s+/i, '');
  }

  return cleaned.trim();
}

/**
 * Validate that a token looks like a valid JWT format (three base64 parts separated by dots)
 */
export function isValidJwtFormat(token: string): boolean {
  if (!token) return false;

  // JWT should have exactly 3 parts separated by dots
  const parts = token.split('.');
  if (parts.length !== 3) return false;

  // Each part should be non-empty and contain only valid base64url characters
  const base64UrlRegex = /^[A-Za-z0-9_-]+$/;
  return parts.every(part => part.length > 0 && base64UrlRegex.test(part));
}

/**
 * Get the raw token from localStorage (cleaned, without "Bearer " prefix)
 */
export function getRawToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const rawToken = localStorage.getItem('token');
  return cleanToken(rawToken);
}

// Request interceptor to add authorization token
// This runs BEFORE every request and ensures the Authorization header is set correctly
const addAuthHeader = (config: any) => {
  // Ensure we're in browser environment
  if (typeof window === 'undefined') {
    return config;
  }

  const rawToken = localStorage.getItem('token');

  // Clean the token to ensure no "Bearer " prefix
  const token = cleanToken(rawToken);

  // Debug logging in development
  if (process.env.NODE_ENV === 'development') {
    console.log('[API Client] Request to:', config.url);
    console.log('[API Client] Token present:', !!token);
    console.log('[API Client] Token length:', token?.length || 0);
  }

  // Always initialize headers object
  config.headers = config.headers || {};

  if (token) {
    // Validate JWT format before sending
    if (!isValidJwtFormat(token)) {
      console.error('[API Client] Invalid JWT format in localStorage. Clearing token.');
      localStorage.removeItem('token');
      config.headers['Content-Type'] = 'application/json';
      return config;
    }

    // Set Authorization header with clean token - ONLY ONE "Bearer" prefix
    config.headers.Authorization = `Bearer ${token}`;
    config.headers['Content-Type'] = 'application/json';

    if (process.env.NODE_ENV === 'development') {
      console.log('[API Client] Authorization header set:', `Bearer ${token.substring(0, 20)}...`);
    }
  } else {
    // For public endpoints (login, register), still set Content-Type
    config.headers['Content-Type'] = 'application/json';

    // Only log warning for protected endpoints (not login/register)
    const isPublicEndpoint = config.url?.includes('/auth/');
    if (!isPublicEndpoint && config.url) {
      console.warn('[API Client] No token found in localStorage for:', config.url);
    }
  }

  return config;
};

// Add interceptors to both clients
apiClient.interceptors.request.use(addAuthHeader);
aiAgentClient.interceptors.request.use(addAuthHeader);

// Response interceptor to handle unauthorized responses
const handleUnauthorized = (error: any) => {
  if (error.response?.status === 401 || error.response?.status === 403) {
    console.error('[API Client] Unauthorized error:', {
      status: error.response.status,
      data: error.response.data,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        hasAuth: !!error.config?.headers?.Authorization,
      },
    });

    // Remove token and redirect to login
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
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
