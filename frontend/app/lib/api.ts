/**
 * API utility functions for making authenticated requests
 * Use these when you need explicit control over headers
 */

const TOKEN_KEY = 'token';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Clean a token by removing any "Bearer " prefix and trimming whitespace.
 * Ensures only the raw JWT is used.
 */
function cleanToken(token: string | null): string | null {
  if (!token) return null;
  
  let cleaned = token.trim();
  
  // Keep removing "Bearer " prefix until none remains
  while (/^Bearer\s+/i.test(cleaned)) {
    cleaned = cleaned.replace(/^Bearer\s+/i, '');
  }
  
  return cleaned.trim();
}

/**
 * Validate that a token looks like a valid JWT format (three base64 parts separated by dots)
 */
function isValidJwtFormat(token: string): boolean {
  if (!token) return false;
  
  const parts = token.split('.');
  if (parts.length !== 3) return false;
  
  const base64UrlRegex = /^[A-Za-z0-9_-]+$/;
  return parts.every(part => part.length > 0 && base64UrlRegex.test(part));
}

/**
 * Get the current auth token from localStorage (cleaned, without "Bearer " prefix)
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const rawToken = localStorage.getItem(TOKEN_KEY);
  return cleanToken(rawToken);
}

/**
 * Get headers for authenticated requests
 * Includes Authorization and Content-Type
 * Ensures the Authorization header is formatted as: "Bearer <token>"
 */
export function getAuthHeaders(customHeaders?: Record<string, string>): Record<string, string> {
  const rawToken = getAuthToken();
  const token = cleanToken(rawToken);

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(customHeaders || {}),
  };

  if (token) {
    // Validate JWT format before adding to headers
    if (!isValidJwtFormat(token)) {
      console.error('[API] Invalid JWT format in localStorage. Clearing token.');
      if (typeof window !== 'undefined') {
        localStorage.removeItem(TOKEN_KEY);
      }
      return headers;
    }
    
    // Set Authorization header with exactly one "Bearer " prefix
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * Make an authenticated fetch request
 * Wrapper around fetch that automatically includes auth headers
 */
export async function authenticatedFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

  const headers = getAuthHeaders(options.headers as Record<string, string>);

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle unauthorized responses
  if (response.status === 401 || response.status === 403) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
      console.error('[API] Authentication failed - token removed');
    }
  }

  return response;
}

/**
 * Typed helper for JSON responses
 */
export async function fetchJson<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await authenticatedFetch(endpoint, options);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
