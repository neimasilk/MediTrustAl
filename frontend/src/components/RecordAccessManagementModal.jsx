import React from 'react';
import {
  Modal,
  Box,
  Typography,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField, // Added TextField
  CircularProgress,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { grantAccessToRecord, revokeAccessFromRecord } from '../services/medicalRecordService'; // Import services

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};

const RecordAccessManagementModal = ({ open, onClose, record }) => {
  const [doctorAddress, setDoctorAddress] = React.useState('');
  const [isLoadingGrant, setIsLoadingGrant] = React.useState(false); // Specific loading for grant
  const [isLoadingRevoke, setIsLoadingRevoke] = React.useState(false); // Specific loading for revoke
  const [message, setMessage] = React.useState({ text: '', type: '' });

  React.useEffect(() => {
    if (open) {
      setDoctorAddress('');
      setIsLoadingGrant(false);
      setIsLoadingRevoke(false);
      setMessage({ text: '', type: '' });
    }
  }, [open, record]);

  if (!record) {
    return null; // Don't render if no record is selected
  }

  const handleGrantAccess = async () => {
    if (!doctorAddress.trim()) {
      setMessage({ text: 'Alamat dokter tidak boleh kosong.', type: 'error' });
      return;
    }
    setIsLoadingGrant(true); // Use specific loader
    setMessage({ text: '', type: '' });

    try {
      const response = await grantAccessToRecord(record.id, doctorAddress.trim());
      setMessage({ text: response.message || `Akses berhasil diberikan kepada ${doctorAddress.trim()}`, type: 'success' });
      // setDoctorAddress(''); // Keep address for potential revoke
    } catch (error) {
      const errorDetail = error.data?.detail || error.message || 'Error tidak diketahui';
      setMessage({ text: `Gagal memberikan akses: ${errorDetail}`, type: 'error' });
    } finally {
      setIsLoadingGrant(false); // Use specific loader
    }
  };

  const handleRevokeAccess = async () => {
    if (!doctorAddress.trim()) {
      setMessage({ text: 'Alamat dokter untuk dicabut tidak boleh kosong.', type: 'error' });
      return;
    }
    setIsLoadingRevoke(true); // Use specific loader
    setMessage({ text: '', type: '' });

    try {
      const response = await revokeAccessFromRecord(record.id, doctorAddress.trim());
      setMessage({ text: response.message || `Akses berhasil dicabut dari ${doctorAddress.trim()}`, type: 'success' });
      // setDoctorAddress(''); // Keep address for potential grant
    } catch (error) {
      // Error structure from revokeAccessFromRecord might be error.response.data.detail
      const errorDetail = error.response?.data?.detail || error.data?.detail || error.message || 'Error tidak diketahui';
      setMessage({ text: `Gagal mencabut akses: ${errorDetail}`, type: 'error' });
    } finally {
      setIsLoadingRevoke(false); // Use specific loader
    }
  };
  
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Manage Access for Record: {record?.id} ({record?.record_type})
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            color: (theme) => theme.palette.grey[500],
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Typography gutterBottom>
          Record Hash: {record?.data_hash || 'N/A'}
        </Typography>
        
        <Box component="form" sx={{ mt: 2, p: 2, border: 1, borderColor: 'grey.300', borderRadius: 1 }}>
          <Typography variant="h6" gutterBottom>
            Grant Access to Doctor
          </Typography>
          <TextField
            label="Alamat Blockchain Dokter"
            value={doctorAddress}
            onChange={(e) => {
              setDoctorAddress(e.target.value);
              setMessage({ text: '', type: '' });
            }}
            fullWidth
            margin="dense"
            disabled={isLoadingGrant || isLoadingRevoke}
          />
          <Box sx={{ display: 'flex', gap: 1, mt: 2 }}> {/* Wrapper for buttons */}
            <Button
              variant="contained"
              color="primary"
              onClick={handleGrantAccess}
              disabled={isLoadingGrant || isLoadingRevoke || !doctorAddress.trim()}
              sx={{ position: 'relative' }}
            >
              Berikan Akses
              {isLoadingGrant && (
                <CircularProgress
                  size={24}
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    marginTop: '-12px',
                    marginLeft: '-12px',
                  }}
                />
              )}
            </Button>
            <Button
              variant="outlined" // Different variant for revoke
              color="secondary"  // Different color for revoke
              onClick={handleRevokeAccess}
              disabled={isLoadingGrant || isLoadingRevoke || !doctorAddress.trim()}
              sx={{ position: 'relative' }}
            >
              Cabut Akses
              {isLoadingRevoke && (
                <CircularProgress
                  size={24}
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    marginTop: '-12px',
                    marginLeft: '-12px',
                  }}
                />
              )}
            </Button>
          </Box>
          {message.text && (
            <Typography 
              color={message.type === 'success' ? 'green' : 'error'} 
              sx={{ mt: 2 }}
            >
              {message.text}
            </Typography>
          )}
        </Box>

        {/* Placeholder for Revoke Access and Current Access List */}
        <Box mt={3} p={2} border={1} borderColor="grey.300" borderRadius={1}>
            <Typography variant="subtitle1" gutterBottom>
                Future Features
            </Typography>
            <Typography variant="body2">
                Revoke access and view current access list functionality will be implemented here.
            </Typography>
        </Box>

      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="secondary">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RecordAccessManagementModal;

