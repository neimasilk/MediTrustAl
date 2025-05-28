// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage'; // Import the new RegisterPage
import DashboardPage from './pages/DashboardPage'; // Import the new DashboardPage
import PrivateRoute from './utils/PrivateRoute';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
// No need to import useDispatch, useSelector, logout, or Button here anymore as they are in DashboardPage

const theme = createTheme({
  // You can customize your theme here if needed
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Ensures consistent baseline styling */}
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<PrivateRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} /> {/* Use the actual DashboardPage */}
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
