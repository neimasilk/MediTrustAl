// frontend/src/pages/LoginPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Container, Box, Typography, TextField, Button, Alert, CircularProgress, Link } from '@mui/material';
import * as authService from '../services/authService';
import { loginStart, loginSuccess, loginFailure, logout } from '../store/slices/authSlice';
import { getErrorMessage, logError, handleAuthError } from '../utils/errorHandler';
// tokenManager is not directly used here anymore for saving, Redux handles it.

const LoginPage = () => {
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isLoading, error } = useSelector((state) => state.auth);

  const handleSubmit = async (event) => {
    event.preventDefault();
    dispatch(loginStart());

    try {
      const response = await authService.loginUser({
        username_or_email: usernameOrEmail,
        password: password,
      });

      if (response && response.status === 200 && response.data && response.data.access_token) {
        // Assuming the API response might also contain user details
        // If not, you might need another API call to fetch user details
        dispatch(loginSuccess({ token: response.data.access_token, user: response.data.user || null }));
        navigate('/dashboard');
      } else {
        const { userMessage } = getErrorMessage({ response });
        logError('Login - Unexpected response', { response }, { usernameOrEmail });
        dispatch(loginFailure({ error: userMessage }));
      }
    } catch (err) {
      // Check if it's an authentication error that requires logout
      if (handleAuthError(err, () => dispatch(logout()))) {
        return; // Auth error handled, don't proceed with normal error handling
      }
      
      const { userMessage } = getErrorMessage(err);
      logError('Login - API call failed', err, { usernameOrEmail });
      dispatch(loginFailure({ error: userMessage }));
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h5">
          Login
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="usernameOrEmail"
            label="Username or Email"
            name="usernameOrEmail"
            autoComplete="email"
            autoFocus
            value={usernameOrEmail}
            onChange={(e) => setUsernameOrEmail(e.target.value)}
            disabled={isLoading}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
          />
          {error && (
            <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
              {/* Ensure error is a string if it's an object */}
              {error}
            </Alert>
          )}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Login'}
          </Button>
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Link href="/register" variant="body2">
              {"Don't have an account? Sign Up"}
            </Link>
          </Box>
        </Box>
      </Box>
    </Container>
  );
};

export default LoginPage;
