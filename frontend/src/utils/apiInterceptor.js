// frontend/src/utils/apiInterceptor.js

import { store } from '../store/store';
import { validateToken, logout } from '../store/slices/authSlice';
import { getToken, isTokenExpired } from './tokenManager';
import { handleAuthError } from './errorHandler';

/**
 * API Request Interceptor
 * Automatically validates token before each request and handles expired tokens
 */
export const setupApiInterceptors = () => {
  // This function can be called to setup interceptors for axios or fetch
  // For now, we'll provide utility functions that can be used in services
};

/**
 * Validates token before making API requests
 * @returns {boolean} True if token is valid, false if expired
 */
export const validateTokenBeforeRequest = () => {
  const token = getToken();
  
  if (!token) {
    return false;
  }
  
  if (isTokenExpired()) {
    // Dispatch validateToken action to update Redux state
    store.dispatch(validateToken());
    
    // Handle auth error (will show notification and redirect)
    handleAuthError(
      { message: 'Session expired' },
      () => store.dispatch(logout())
    );
    
    return false;
  }
  
  return true;
};

/**
 * Gets authorization header with current valid token
 * @returns {Object|null} Authorization header object or null if no valid token
 */
export const getAuthHeader = () => {
  if (!validateTokenBeforeRequest()) {
    return null;
  }
  
  const token = getToken();
  return {
    'Authorization': `Bearer ${token}`
  };
};

/**
 * Wrapper for fetch requests with automatic token validation
 * @param {string} url - Request URL
 * @param {Object} options - Fetch options
 * @returns {Promise} Fetch promise
 */
export const authenticatedFetch = async (url, options = {}) => {
  // Validate token before request
  if (!validateTokenBeforeRequest()) {
    throw new Error('Authentication required');
  }
  
  // Add auth header
  const authHeader = getAuthHeader();
  if (!authHeader) {
    throw new Error('No valid authentication token');
  }
  
  const requestOptions = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeader,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, requestOptions);
    
    // Handle 401/403 responses (token might be invalid on server side)
    if (response.status === 401 || response.status === 403) {
      handleAuthError(
        { message: 'Authentication failed' },
        () => store.dispatch(logout())
      );
      throw new Error('Authentication failed');
    }
    
    return response;
  } catch (error) {
    // Re-throw the error for handling by the calling code
    throw error;
  }
};

/**
 * Periodically check token expiry (can be used in App.jsx)
 * @param {number} intervalMs - Check interval in milliseconds (default: 60000 = 1 minute)
 */
export const startTokenExpiryCheck = (intervalMs = 60000) => {
  const checkInterval = setInterval(() => {
    const state = store.getState();
    
    // Only check if user is authenticated
    if (state.auth.isAuthenticated) {
      store.dispatch(validateToken());
    } else {
      // Clear interval if user is not authenticated
      clearInterval(checkInterval);
    }
  }, intervalMs);
  
  return checkInterval;
};