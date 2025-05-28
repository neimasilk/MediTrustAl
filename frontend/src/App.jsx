// frontend/src/App.jsx
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import PrivateRoute from './utils/PrivateRoute';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { startTokenExpiryCheck } from './utils/apiInterceptor';
import { useSelector } from 'react-redux';

const theme = createTheme({
  // You can customize your theme here if needed
});

function App() {
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);

  useEffect(() => {
    let tokenCheckInterval;
    
    // Start token expiry checking if user is authenticated
    if (isAuthenticated) {
      tokenCheckInterval = startTokenExpiryCheck(60000); // Check every minute
    }
    
    // Cleanup interval on unmount or when authentication status changes
    return () => {
      if (tokenCheckInterval) {
        clearInterval(tokenCheckInterval);
      }
    };
  }, [isAuthenticated]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Ensures consistent baseline styling */}
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<PrivateRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            {/* Other private routes will go here */}
          </Route>
          {/* Default to dashboard if authenticated, else PrivateRoute handles redirect to login */}
          <Route path="/" element={<Navigate replace to="/dashboard" />} /> 
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
