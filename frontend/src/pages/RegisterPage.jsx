// frontend/src/pages/RegisterPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Container, Box, Typography, TextField, Button, Alert, CircularProgress, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import * as authService from '../services/authService';
import { getErrorMessage, logError } from '../utils/errorHandler';
import { registerStart, registerSuccess, registerFailure } from '../store/slices/authSlice';

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState(''); // Added fullName state
  const [role, setRole] = useState('PATIENT'); // Added role state with default
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isLoading, error } = useSelector((state) => state.auth);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      dispatch(registerFailure({ error: 'Passwords do not match.' }));
      return;
    }
    dispatch(registerStart());

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
        dispatch(registerSuccess());
        console.log('Registration successful, navigating to login.');
        navigate('/login?registrationSuccess=true'); // Redirect to login with a success message
      } else {
        const { userMessage } = getErrorMessage({ response });
        logError('Registration - Unexpected response', { response }, { username, email, fullName, role });
        dispatch(registerFailure({ error: userMessage }));
      }
    } catch (err) {
      const { userMessage } = getErrorMessage(err);
      logError('Registration - API call failed', err, { username, email, fullName, role });
      dispatch(registerFailure({ error: userMessage }));
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