// frontend/src/store/slices/authSlice.js
import { createSlice } from '@reduxjs/toolkit';
import { getToken, saveToken, removeToken } from '../../utils/tokenManager';

const initialState = {
  isAuthenticated: !!getToken(),
  token: getToken(),
  user: null, // Or attempt to get from localStorage if stored
  isLoading: false,
  error: null,
};

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
      saveToken(action.payload.token);
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
  },
});

export const { loginStart, loginSuccess, loginFailure, logout } = authSlice.actions;
export default authSlice.reducer;
