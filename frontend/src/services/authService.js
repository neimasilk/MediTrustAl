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
    const response = await axios.post('http://localhost:8000/api/v1/auth/login/json', credentials, {
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
