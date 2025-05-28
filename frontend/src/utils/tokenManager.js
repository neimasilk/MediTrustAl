// frontend/src/utils/tokenManager.js

// Token storage configuration
const TOKEN_KEY = 'authToken';
const TOKEN_EXPIRY_KEY = 'authTokenExpiry';

/**
 * Saves the token to localStorage with expiry information.
 * 
 * WARNING: localStorage is vulnerable to XSS attacks. In production, consider:
 * - Using httpOnly cookies for token storage
 * - Implementing proper CSP headers
 * - Using secure, sameSite cookie attributes
 * - Implementing token refresh mechanism
 * 
 * @param {string} token - The authentication token.
 * @param {number} expiryMinutes - Token expiry in minutes (default: 30)
 */
export const saveToken = (token, expiryMinutes = 30) => {
  try {
    const expiryTime = new Date().getTime() + (expiryMinutes * 60 * 1000);
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());
  } catch (error) {
    console.error('Error saving token to localStorage:', error);
  }
};

/**
 * Retrieves the token from localStorage and checks if it's expired.
 * @returns {string|null} The authentication token, or null if not found, expired, or error occurs.
 */
export const getToken = () => {
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    const expiryTime = localStorage.getItem(TOKEN_EXPIRY_KEY);
    
    if (!token) {
      return null;
    }
    
    // Check if token is expired
    if (expiryTime) {
      const now = new Date().getTime();
      if (now > parseInt(expiryTime)) {
        // Token expired, remove it
        removeToken();
        return null;
      }
    }
    
    return token;
  } catch (error) {
    console.error('Error retrieving token from localStorage:', error);
    return null;
  }
};

/**
 * Checks if the current token is expired without removing it.
 * @returns {boolean} True if token is expired or doesn't exist.
 */
export const isTokenExpired = () => {
  try {
    const expiryTime = localStorage.getItem(TOKEN_EXPIRY_KEY);
    if (!expiryTime) {
      return true;
    }
    
    const now = new Date().getTime();
    return now > parseInt(expiryTime);
  } catch (error) {
    console.error('Error checking token expiry:', error);
    return true;
  }
};

/**
 * Removes the token and expiry information from localStorage.
 */
export const removeToken = () => {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
  } catch (error) {
    console.error('Error removing token from localStorage:', error);
  }
};
