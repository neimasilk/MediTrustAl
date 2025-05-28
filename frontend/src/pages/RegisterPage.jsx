// frontend/src/pages/RegisterPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { Container, Box, Typography, TextField, Button, Alert, CircularProgress, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import * as authService from '../services/authService';
// Placeholder for registration-specific actions if needed in Redux
// import { registerStart, registerSuccess, registerFailure } from '../store/slices/authSlice'; 

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState(''); // Added fullName state
  const [role, setRole] = useState('PATIENT'); // Added role state with default
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const dispatch = useDispatch(); // Keep dispatch if you plan to use Redux for registration state

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setIsLoading(true);
    setError('');

    try {
      console.log('Submitting registration with:', { username, email, fullName, role, password }); // Log data yang dikirim
      const response = await authService.registerUser({
        username,
        email,
        full_name: fullName, // Changed to match backend expectation
        role,
        password,
      });

      console.log('Registration response:', response); // Log respons dari server

      if (response && response.status === 201) { // Assuming 201 Created for successful registration
        // Optionally, log the user in directly or navigate to login page
        // dispatch(registerSuccess({ user: response.data.user, token: response.data.access_token }));
        console.log('Registration successful, navigating to login.');
        navigate('/login?registrationSuccess=true'); // Redirect to login with a success message
      } else {
        let errorMessage = 'Registration failed. Please try again.';
        if (response && response.data && (response.data.detail || response.data.message)) {
          errorMessage = response.data.detail || response.data.message;
        }
        console.error('Registration failed with error message:', errorMessage, 'Response data:', response ? response.data : 'No response data');
        setError(errorMessage);
      }
    } catch (err) {
      console.error('An unexpected error occurred during registration:', err);
      setError('An unexpected error occurred during registration.');
      console.error('Full registration error object:', err.response || err.message || err);
    } finally {
      console.log('Finished registration attempt, setting isLoading to false.');
      setIsLoading(false);
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
          Sign Up
        </Typography>
        {error && <Alert severity="error" sx={{ mt: 2, width: '100%' }}>{error}</Alert>}
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="username"
            label="Username"
            name="username"
            autoComplete="username"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="fullName"
            label="Full Name"
            name="fullName"
            autoComplete="name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="confirmPassword"
            label="Confirm Password"
            type="password"
            id="confirmPassword"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          <FormControl fullWidth margin="normal" required>
            <InputLabel id="role-select-label">Role</InputLabel
            <Select
              labelId="role-select-label"
              id="role"
              value={role}
              label="Role"
              onChange={(e) => setRole(e.target.value)}
            >
              <MenuItem value="PATIENT">Patient</MenuItem>
              <MenuItem value="DOCTOR">Doctor</MenuItem>
              {/* <MenuItem value="ADMIN">Admin</MenuItem> */}
            </Select>
          </FormControl>
          <TextField
            margin="normal"
            required
            fullWidth
            name="confirmPassword"
            label="Confirm Password"
            type="password"
            id="confirmPassword"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Sign Up'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default RegisterPage;