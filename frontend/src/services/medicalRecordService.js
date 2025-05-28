// frontend/src/services/medicalRecordService.js
import axios from 'axios';
import { getToken } from '../utils/tokenManager';
import { authenticatedFetch, validateTokenBeforeRequest, getAuthHeader } from '../utils/apiInterceptor';

/**
 * Fetches the medical records for the currently authenticated patient.
 * @returns {Promise<object>} The response from the server.
 */
export const getMyMedicalRecords = async () => {
  // Validate token before making request
  if (!validateTokenBeforeRequest()) {
    return Promise.reject({ 
      status: 401,
      data: { detail: 'Authentication required' }
    });
  }

  try {
    const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const response = await authenticatedFetch(`${apiUrl}/medical-records/patient/me`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
      return Promise.reject({
        status: response.status,
        data: errorData
      });
    }
    
    const data = await response.json();
    return { data }; // Mimic axios response structure
  } catch (error) {
    console.error('Failed to fetch medical records:', error.message);
    return Promise.reject({ 
      status: 500,
      data: { detail: error.message || 'An unexpected error occurred while fetching records.' } 
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
  // Validate token before making request
  if (!validateTokenBeforeRequest()) {
    return Promise.reject({ 
      status: 401,
      data: { detail: 'Authentication required' }
    });
  }

  try {
    const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const response = await authenticatedFetch(
      `${apiUrl}/medical-records/${recordId}/grant-access`,
      {
        method: 'POST',
        body: JSON.stringify({ doctor_address: doctorAddress }),
      }
    );
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
      return Promise.reject({
        status: response.status,
        data: errorData
      });
    }
    
    const data = await response.json();
    return data; // Return data directly on success
  } catch (error) {
    console.error('Failed to grant access to medical record:', error.message);
    return Promise.reject({ 
      status: 500, 
      data: { detail: error.message || 'An unexpected error occurred while granting access.' } 
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
  // Validate token before making request
  if (!validateTokenBeforeRequest()) {
    return Promise.reject({ 
      status: 401,
      data: { detail: 'Authentication required' }
    });
  }

  try {
    const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const response = await authenticatedFetch(
      `${apiUrl}/medical-records/${recordId}/revoke-access`,
      {
        method: 'POST',
        body: JSON.stringify({ doctor_address: doctorAddress }),
      }
    );
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
      return Promise.reject({
        status: response.status,
        data: errorData
      });
    }
    
    const data = await response.json();
    return data; // Return data directly on success
  } catch (error) {
    console.error('Failed to revoke access from medical record:', error.message);
    return Promise.reject({ 
      status: 500, 
      data: { detail: error.message || 'An unexpected error occurred while revoking access.' } 
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
  // Validate token before making request
  if (!validateTokenBeforeRequest()) {
    return Promise.reject({ 
      status: 401,
      data: { detail: 'Authentication required' }
    });
  }

  try {
    const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const response = await authenticatedFetch(
      `${apiUrl}/medical-records/${recordId}/check-access/${doctorAddress}`
    );
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
      return Promise.reject({
        status: response.status,
        data: errorData
      });
    }
    
    const data = await response.json();
    return data; // Return data directly on success
  } catch (error) {
    console.error('Failed to check access for medical record:', error.message);
    return Promise.reject({ 
      status: 500, 
      data: { detail: error.message || 'An unexpected error occurred while checking access.' } 
    });
  }
};
