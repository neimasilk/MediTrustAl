// frontend/src/pages/DashboardPage.jsx
import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logout } from '../store/slices/authSlice';
import { getMyMedicalRecords } from '../services/medicalRecordService';
import {
  Button, Container, Typography, Box, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper,
  Alert, CircularProgress
} from '@mui/material';

const DashboardPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth); // Get user info if needed

  const [records, setRecords] = useState([]);
  const [isLoadingRecords, setIsLoadingRecords] = useState(true);
  const [errorRecords, setErrorRecords] = useState(null);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  useEffect(() => {
    const fetchRecords = async () => {
      setIsLoadingRecords(true);
      setErrorRecords(null);
      try {
        const response = await getMyMedicalRecords();
        setRecords(response.data || []); // Ensure response.data is not undefined
      } catch (error) {
        const errorMessage = error.data?.detail || error.message || 'Failed to fetch records';
        setErrorRecords(errorMessage);
        if (error.status === 401 || error.status === 403 || error.message === 'No token found') {
          // If unauthorized or token is invalid/missing, logout user
          dispatch(logout());
          navigate('/login');
        }
      } finally {
        setIsLoadingRecords(false);
      }
    };

    fetchRecords();
  }, [dispatch, navigate]);

  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return 'N/A';
    try {
      return new Date(dateTimeString).toLocaleString();
    } catch (e) {
      return 'Invalid Date';
    }
  };

  return (
    <Container component="main" maxWidth="lg">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h4" gutterBottom>
          Welcome to your Dashboard{user && user.username ? `, ${user.username}` : ''}!
        </Typography>
        <Button variant="contained" color="primary" onClick={handleLogout} sx={{ mb: 4 }}>
          Logout
        </Button>

        <Typography component="h2" variant="h5" gutterBottom>
          Your Medical Records
        </Typography>

        {isLoadingRecords && <CircularProgress sx={{ mt: 4 }} />}

        {!isLoadingRecords && errorRecords && (
          <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
            {errorRecords}
          </Alert>
        )}

        {!isLoadingRecords && !errorRecords && records.length > 0 && (
          <TableContainer component={Paper} sx={{ mt: 2 }}>
            <Table sx={{ minWidth: 650 }} aria-label="simple table">
              <TableHead>
                <TableRow>
                  <TableCell>Record ID</TableCell>
                  <TableCell>Record Type</TableCell>
                  <TableCell>Created At</TableCell>
                  <TableCell>Data Hash</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {records.map((record) => (
                  <TableRow
                    key={record.id}
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      {record.id}
                    </TableCell>
                    <TableCell>{record.record_type}</TableCell>
                    <TableCell>{formatDateTime(record.created_at)}</TableCell>
                    <TableCell sx={{ wordBreak: 'break-all' }}>{record.data_hash}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {!isLoadingRecords && !errorRecords && records.length === 0 && (
          <Typography sx={{ mt: 4 }}>
            You have no medical records.
          </Typography>
        )}
      </Box>
    </Container>
  );
};

export default DashboardPage;
