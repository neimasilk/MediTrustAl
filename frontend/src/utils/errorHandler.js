/**
 * Utility functions for consistent error handling across the frontend
 */

/**
 * Extract user-friendly error message from API response
 * @param {Error|Object} error - The error object from API call
 * @returns {string} User-friendly error message
 */
export const getErrorMessage = (error) => {
  // Default fallback message
  let userMessage = 'An unexpected error occurred. Please try again.';
  let technicalDetails = null;

  try {
    if (error?.response?.data) {
      // API returned structured error
      const errorData = error.response.data;
      
      if (errorData.detail) {
        userMessage = errorData.detail;
      } else if (errorData.message) {
        userMessage = errorData.message;
      } else if (Array.isArray(errorData) && errorData.length > 0) {
        // Validation errors array
        userMessage = errorData.map(err => err.msg || err.message || err).join(', ');
      }
      
      technicalDetails = {
        status: error.response.status,
        statusText: error.response.statusText,
        data: errorData
      };
    } else if (error?.response?.status) {
      // HTTP error without detailed message
      const status = error.response.status;
      switch (status) {
        case 400:
          userMessage = 'Invalid request. Please check your input.';
          break;
        case 401:
          userMessage = 'Authentication failed. Please log in again.';
          break;
        case 403:
          userMessage = 'Access denied. You do not have permission for this action.';
          break;
        case 404:
          userMessage = 'The requested resource was not found.';
          break;
        case 409:
          userMessage = 'Conflict detected. The resource may already exist.';
          break;
        case 422:
          userMessage = 'Validation error. Please check your input data.';
          break;
        case 429:
          userMessage = 'Too many requests. Please wait a moment and try again.';
          break;
        case 500:
          userMessage = 'Server error. Please try again later.';
          break;
        case 503:
          userMessage = 'Service temporarily unavailable. Please try again later.';
          break;
        default:
          userMessage = `Error ${status}: ${error.response.statusText || 'Unknown error'}`;
      }
      
      technicalDetails = {
        status: error.response.status,
        statusText: error.response.statusText
      };
    } else if (error?.message) {
      // Network or other errors
      if (error.message.includes('Network Error')) {
        userMessage = 'Network connection failed. Please check your internet connection.';
      } else if (error.message.includes('timeout')) {
        userMessage = 'Request timed out. Please try again.';
      } else {
        userMessage = error.message;
      }
      
      technicalDetails = { originalMessage: error.message };
    }
  } catch (parseError) {
    console.error('Error parsing error message:', parseError);
    userMessage = 'An unexpected error occurred. Please try again.';
  }

  return { userMessage, technicalDetails };
};

/**
 * Log error details to console for debugging (only in development)
 * @param {string} context - Context where the error occurred
 * @param {Error|Object} error - The error object
 * @param {Object} additionalInfo - Additional context information
 */
export const logError = (context, error, additionalInfo = {}) => {
  if (process.env.NODE_ENV === 'development') {
    console.group(`🚨 Error in ${context}`);
    console.error('Error object:', error);
    if (Object.keys(additionalInfo).length > 0) {
      console.error('Additional info:', additionalInfo);
    }
    if (error?.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    console.groupEnd();
  }
};

/**
 * Handle authentication errors specifically
 * @param {Error|Object} error - The error object
 * @param {Function} logoutCallback - Function to call for logout
 * @returns {boolean} True if auth error was handled
 */
export const handleAuthError = (error, logoutCallback) => {
  if (error?.response?.status === 401) {
    // Token expired or invalid
    if (logoutCallback && typeof logoutCallback === 'function') {
      logoutCallback();
    }
    return true;
  }
  return false;
};

/**
 * Create a standardized error notification object
 * @param {Error|Object} error - The error object
 * @param {string} context - Context where the error occurred
 * @returns {Object} Notification object with type and message
 */
export const createErrorNotification = (error, context = '') => {
  const { userMessage, technicalDetails } = getErrorMessage(error);
  
  logError(context, error, { userMessage, technicalDetails });
  
  return {
    type: 'error',
    message: userMessage,
    duration: 6000, // Show error messages longer
    technical: technicalDetails
  };
};

/**
 * Create a success notification object
 * @param {string} message - Success message
 * @returns {Object} Notification object
 */
export const createSuccessNotification = (message) => {
  return {
    type: 'success',
    message,
    duration: 4000
  };
};