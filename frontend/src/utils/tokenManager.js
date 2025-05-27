// frontend/src/utils/tokenManager.js

/**
 * Saves the token to localStorage.
 * @param {string} token - The authentication token.
 */
export const saveToken = (token) => {
  try {
    localStorage.setItem('authToken', token);
  } catch (error) {
    console.error('Error saving token to localStorage:', error);
  }
};

/**
 * Retrieves the token from localStorage.
 * @returns {string|null} The authentication token, or null if not found or an error occurs.
 */
export const getToken = () => {
  try {
    return localStorage.getItem('authToken');
  } catch (error) {
    console.error('Error retrieving token from localStorage:', error);
    return null;
  }
};

/**
 * Removes the token from localStorage.
 */
export const removeToken = () => {
  try {
    localStorage.removeItem('authToken');
  } catch (error) {
    console.error('Error removing token from localStorage:', error);
  }
};
