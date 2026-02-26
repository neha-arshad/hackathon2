'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';

const TOKEN_KEY = 'token';

/**
 * Clean a token by removing any "Bearer " prefix and trimming whitespace.
 * Ensures only the raw JWT is stored.
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
 * Custom hook for managing authentication state
 * Provides token access, validation, and logout functionality
 */
export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check if token exists and is valid
  const checkAuth = useCallback(() => {
    if (typeof window === 'undefined') {
      return false;
    }

    const rawToken = localStorage.getItem(TOKEN_KEY);
    const token = cleanToken(rawToken);

    if (!token) {
      setIsAuthenticated(false);
      setIsLoading(false);
      return false;
    }

    // Validate JWT format
    if (!isValidJwtFormat(token)) {
      console.error('[useAuth] Invalid JWT format in localStorage. Clearing token.');
      localStorage.removeItem(TOKEN_KEY);
      setIsAuthenticated(false);
      setIsLoading(false);
      return false;
    }

    // Optionally check token expiration
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const isExpired = payload.exp && payload.exp < Date.now() / 1000;

      if (isExpired) {
        localStorage.removeItem(TOKEN_KEY);
        setIsAuthenticated(false);
        setIsLoading(false);
        return false;
      }

      setIsAuthenticated(true);
      setIsLoading(false);
      return true;
    } catch (e) {
      // Invalid token format or decoding error
      console.error('[useAuth] Error parsing token:', e);
      localStorage.removeItem(TOKEN_KEY);
      setIsAuthenticated(false);
      setIsLoading(false);
      return false;
    }
  }, []);

  // Get the current token (cleaned, without "Bearer " prefix)
  const getToken = useCallback(() => {
    if (typeof window === 'undefined') {
      return null;
    }
    const rawToken = localStorage.getItem(TOKEN_KEY);
    return cleanToken(rawToken);
  }, []);

  // Store token after login - ensures ONLY the raw JWT is stored
  const setToken = useCallback((token: string) => {
    if (typeof window === 'undefined') {
      return;
    }
    // Clean the token before storing to ensure no "Bearer " prefix
    const clean = cleanToken(token);
    
    if (clean && isValidJwtFormat(clean)) {
      localStorage.setItem(TOKEN_KEY, clean);
      setIsAuthenticated(true);
    } else {
      console.error('[useAuth] Attempted to store invalid token format');
    }
  }, []);

  // Remove token and logout
  const logout = useCallback(() => {
    if (typeof window === 'undefined') {
      return;
    }
    localStorage.removeItem(TOKEN_KEY);
    setIsAuthenticated(false);
  }, []);

  // Initial auth check on mount
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return {
    isAuthenticated,
    isLoading,
    getToken,
    setToken,
    logout,
    checkAuth,
  };
}

/**
 * Higher-order component to protect routes that require authentication
 * Usage: export default withAuth(DashboardPage);
 */
export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>
) {
  return function AuthenticatedComponent(props: P) {
    const router = useRouter();
    const { isAuthenticated, isLoading } = useAuth();

    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        router.push('/auth/login');
      }
    }, [isAuthenticated, isLoading, router]);

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        </div>
      );
    }

    if (!isAuthenticated) {
      return null;
    }

    return <WrappedComponent {...props} />;
  };
}
