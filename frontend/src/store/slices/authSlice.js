// frontend/src/store/slices/authSlice.js
import { createSlice } from '@reduxjs/toolkit';
import { saveToken, getToken, removeToken, isTokenExpired } from '../../utils/tokenManager';

// Check token validity on initialization
const token = getToken();
const isValidToken = token && !isTokenExpired();

const initialState = {
  isAuthenticated: isValidToken,
  token: isValidToken ? token : null,
  user: null, // Or attempt to get from localStorage if stored
  isLoading: false,
  error: null,
};

// Clear invalid token on initialization
if (token && isTokenExpired()) {
  removeToken();
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart(state) {
      state.isLoading = true;
      state.error = null;
    },
    loginSuccess(state, action) {
      state.isLoading = false;
      state.isAuthenticated = true;
      state.token = action.payload.token;
      state.user = action.payload.user || null; // Assuming user might be part of payload
      // Save token with 30 minutes expiry (can be configured)
      saveToken(action.payload.token, 30);
    },
    loginFailure(state, action) {
      state.isLoading = false;
      state.isAuthenticated = false;
      state.error = action.payload.error;
      state.token = null;
      state.user = null;
      removeToken();
    },
    logout(state) {
      state.isAuthenticated = false;
      state.token = null;
      state.user = null;
      state.error = null;
      removeToken();
    },
    validateToken(state) {
      // Check if current token is expired
      if (state.token && isTokenExpired()) {
        // Token expired, logout user
        state.isAuthenticated = false;
        state.token = null;
        state.user = null;
        state.error = 'Session expired. Please login again.';
        removeToken();
      }
    },
    registerStart(state) {
      state.isLoading = true;
      state.error = null;
    },
    registerSuccess(state, action) {
      state.isLoading = false;
      state.isAuthenticated = false; // User is registered, not logged in
      // Optionally, store registration success message or user data if API returns it
      // For now, just manage loading/error state
    },
    registerFailure(state, action) {
      state.isLoading = false;
      state.error = action.payload.error;
    },
  },
});

export const { loginStart, loginSuccess, loginFailure, logout, validateToken, registerStart, registerSuccess, registerFailure } = authSlice.actions;
export default authSlice.reducer;
