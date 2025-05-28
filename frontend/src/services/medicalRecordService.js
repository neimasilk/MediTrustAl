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
    const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const response = await axios.get(`${apiUrl}/medical-records/patient/me`, {
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

/**
 * Grants access to a specific medical record for a given doctor.
 * @param {string} recordId - The ID of the medical record.
 * @param {string} doctorAddress - The blockchain address of the doctor to grant access to.
 * @returns {Promise<object>} The response from the server.
 */
export const grantAccessToRecord = async (recordId, doctorAddress) => {
  const token = getToken();
  if (!token) {
    return Promise.reject('No token found');
  }

  try {
const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const response = await axios.post(
      `${apiUrl}/medical-records/${recordId}/grant-access`,
      { doctor_address: doctorAddress },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data; // Return data directly on success
  } catch (error) {
    console.error('Failed to grant access to medical record:', error.response || error.message);
    return Promise.reject(error.response || { 
      status: 500, 
      data: { detail: 'An unexpected error occurred while granting access.' } 
    });
  }
};

/**
 * Revokes access from a specific medical record for a given doctor.
 * @param {string} recordId - The ID of the medical record.
 * @param {string} doctorAddress - The blockchain address of the doctor to revoke access from.
 * @returns {Promise<object>} The response from the server.
 */
export const revokeAccessFromRecord = async (recordId, doctorAddress) => {
  const token = getToken();
  if (!token) {
    return Promise.reject('No token found');
  }

  try {
const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const response = await axios.post(
      `${apiUrl}/medical-records/${recordId}/revoke-access`,
      { doctor_address: doctorAddress },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data; // Return data directly on success
  } catch (error) {
    console.error('Failed to revoke access from medical record:', error.response || error.message);
    return Promise.reject(error.response || { 
      status: 500, 
      data: { detail: 'An unexpected error occurred while revoking access.' } 
    });
  }
};

/**
 * Checks if a doctor has access to a specific medical record.
 * @param {string} recordId - The ID of the medical record.
 * @param {string} doctorAddress - The blockchain address of the doctor.
 * @returns {Promise<object>} The response from the server, typically indicating access status.
 */
export const checkRecordAccessForDoctor = async (recordId, doctorAddress) => {
  const token = getToken();
  if (!token) {
    return Promise.reject('No token found');
  }

  try {
const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const response = await axios.get(
      `${apiUrl}/medical-records/${recordId}/check-access/${doctorAddress}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );
    return response.data; // Return data directly on success
  } catch (error) {
    console.error('Failed to check access for medical record:', error.response || error.message);
    return Promise.reject(error.response || { 
      status: 500, 
      data: { detail: 'An unexpected error occurred while checking access.' } 
    });
  }
};
