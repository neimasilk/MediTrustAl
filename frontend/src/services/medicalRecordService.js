// frontend/src/services/medicalRecordService.js
import axios from 'axios';
import { getToken } from '../utils/tokenManager';

/**
 * Fetches the medical records for the currently authenticated patient.
 * @returns {Promise<object>} The response from the server.
 */
export const getMyMedicalRecords = async () => {
  const token = getToken();

  if (!token) {
    return Promise.reject('No token found');
  }

  try {
    const response = await axios.get('http://localhost:8000/api/v1/medical-records/patient/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response;
  } catch (error) {
    console.error('Failed to fetch medical records:', error.response || error.message);
    // Return the error response from axios, or a custom error object if no response
    return Promise.reject(error.response || { 
      status: 500, // or some other default error code
      data: { detail: 'An unexpected error occurred while fetching records.' } 
    });
  }
};
