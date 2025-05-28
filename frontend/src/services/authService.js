// frontend/src/services/authService.js
import axios from 'axios';

/**
 * Logs in a user.
 * @param {object} credentials - The user's credentials.
 * @param {string} credentials.username_or_email - The username or email.
 * @param {string} credentials.password - The password.
 * @returns {Promise<object>} The response from the server.
 */
export const loginUser = async (credentials) => {
  try {
    const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const response = await axios.post(`${apiUrl}/auth/login/json`, credentials, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response;
  } catch (error) {
    console.error('Login failed:', error.response || error.message);
    // Return the error response from axios, or a custom error object if no response
    return error.response || { 
      status: 500, // or some other default error code
      data: { message: 'An unexpected error occurred.' } 
    };
  }
};

/**
 * Registers a new user.
 * @param {object} userData - The user's registration data.
 * @param {string} userData.username - The username.
 * @param {string} userData.email - The email.
 * @param {string} userData.password - The password.
 * @returns {Promise<object>} The response from the server.
 */
export const registerUser = async (userData) => {
  try {
    const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    // Adjust the endpoint if your backend has a different registration URL
    const response = await axios.post(`${apiUrl}/auth/register`, userData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response;
  } catch (error) {
    console.error('Registration failed:', error.response || error.message);
    return error.response || { 
      status: 500, 
      data: { message: 'An unexpected error occurred during registration.' } 
    };
  }
};
