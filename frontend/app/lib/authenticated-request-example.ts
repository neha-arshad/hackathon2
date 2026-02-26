/**
 * PRODUCTION-READY AUTHENTICATED REQUEST EXAMPLES
 * 
 * These examples show how to make authenticated requests with proper
 * Authorization header handling. The key points are:
 * 
 * 1. Token is stored WITHOUT "Bearer " prefix in localStorage
 * 2. Authorization header is set with EXACTLY ONE "Bearer " prefix
 * 3. Token is cleaned before storage and before use
 * 
 * Expected header format: Authorization: Bearer <actual_token>
 */

// ============================================================================
// AXIOS EXAMPLE (using api-client.ts interceptor)
// ============================================================================

import { apiClient, cleanToken } from '../api-client';

/**
 * Example 1: POST /tasks using axios (recommended approach)
 * The interceptor automatically adds the Authorization header
 */
export async function createTaskWithAxios(
  title: string,
  description: string,
  priority: string
) {
  try {
    const response = await apiClient.post('/tasks', {
      title,
      description,
      priority,
    });
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      console.error('Authentication failed - token may be invalid');
      localStorage.removeItem('token');
    }
    throw error;
  }
}

/**
 * Example 2: GET /tasks using axios
 */
export async function getTasksWithAxios() {
  try {
    const response = await apiClient.get('/tasks');
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      console.error('Authentication failed');
      localStorage.removeItem('token');
    }
    throw error;
  }
}

// ============================================================================
// FETCH EXAMPLE (manual header handling)
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Get the raw token from localStorage (cleaned, without "Bearer " prefix)
 */
function getRawToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const rawToken = localStorage.getItem('token');
  return cleanToken(rawToken);
}

/**
 * Get headers for authenticated requests
 * Ensures Authorization header has EXACTLY ONE "Bearer " prefix
 */
function getAuthHeaders(): HeadersInit {
  const token = getRawToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    // Add Authorization header with exactly one "Bearer " prefix
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * Example 3: POST /tasks using fetch
 */
export async function createTaskWithFetch(
  title: string,
  description: string,
  priority: string
) {
  const response = await fetch(`${API_BASE_URL}/tasks`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ title, description, priority }),
  });

  if (response.status === 401) {
    console.error('Authentication failed');
    localStorage.removeItem('token');
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Example 4: GET /tasks using fetch
 */
export async function getTasksWithFetch() {
  const response = await fetch(`${API_BASE_URL}/tasks`, {
    headers: getAuthHeaders(),
  });

  if (response.status === 401) {
    console.error('Authentication failed');
    localStorage.removeItem('token');
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ============================================================================
// LOGIN EXAMPLE (storing token correctly)
// ============================================================================

/**
 * Example 5: Login and store token correctly
 * IMPORTANT: Store ONLY the raw JWT, without "Bearer " prefix
 */
export async function loginAndStoreToken(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  const data = await response.json();
  const rawToken = data.access_token.trim();

  // CRITICAL: Clean the token to remove any "Bearer " prefix
  // This ensures we store ONLY the raw JWT
  const cleanTokenValue = cleanToken(rawToken);
  
  // Double-check: ensure no "Bearer " prefix remains
  const finalToken = cleanTokenValue?.replace(/^Bearer\s+/i, '').trim() || '';

  // Store the clean token
  localStorage.setItem('token', finalToken);

  console.log('[Login] Token stored successfully');
  return data;
}

// ============================================================================
// KEY POINTS TO REMEMBER
// ============================================================================

/**
 * DO:
 * - Store token WITHOUT "Bearer " prefix: localStorage.setItem('token', 'eyJhbG...')
 * - Let the interceptor add "Bearer " automatically
 * - Use cleanToken() before storing any token
 * - Validate JWT format (3 parts separated by dots)
 * 
 * DON'T:
 * - Store token WITH "Bearer " prefix: localStorage.setItem('token', 'Bearer eyJhbG...')
 * - Manually add "Bearer " if using axios interceptor
 * - Store tokens that don't have valid JWT format
 * 
 * Expected Authorization header:
 * Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
 * 
 * NOT:
 * Authorization: Bearer Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
 */
