import { Grid, Paper, IconButton, Box, Snackbar, Alert } from '@mui/material';
import { useState, useEffect, useCallback } from 'react';
import { styled } from '@mui/material/styles';
import ListIcon from '@mui/icons-material/List';
import { RefreshRounded } from '@mui/icons-material';
import Button from '@mui/material/Button';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { useOrdersStore } from '../store/ordersStore';
import OrdersList from '../components/orders/OrdersList';
import OrderDetail from '../components/orders/OrderDetail';
import OrderItems from '../components/orders/OrderItems';
import { useTranslation } from 'react-i18next';

const ToggleButton = styled(Box)(({ theme }) => ({
  position: 'fixed',
  left: 0,
  top: '25%',
  transform: 'translateY(-50%)',
  zIndex: 1100,
  backgroundColor: theme.palette.background.paper,
  borderRadius: '0 24px 24px 0',
  boxShadow: theme.shadows[3],
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  }
}));

export const OrdersPage = () => {
  const { t } = useTranslation();
  const { selectedOrderId, fetchOrdersfromAPI, syncPackedOrders, fetchOrders } = useOrdersStore();
  const [isListOpen, setIsListOpen] = useState(true);

  // --- SIMPLIFIED GLOBAL SNACKBAR STATE AND LOGIC ---
  const [isSnackbarOpen, setIsSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'info' | 'error' | 'warning'>('info');

  // Function to show a single snackbar message
  const showSnackbar = useCallback((message: string, severity: 'success' | 'info' | 'error' | 'warning') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setIsSnackbarOpen(true);
    // Material UI's Snackbar autoHideDuration will automatically call onClose after 6 seconds
  }, []);

  // Handle closing of the single Snackbar
  const handleSnackbarClose = useCallback((event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setIsSnackbarOpen(false);
  }, []);
  // --- END SIMPLIFIED GLOBAL SNACKBAR LOGIC ---

  const handleFetchOrders = useCallback(() => {
    fetchOrders();
    showSnackbar(t('refreshing_orders'), 'info');
  }, [fetchOrders, showSnackbar, t]);

  const handlesyncPackedOrders = useCallback(() => {
    syncPackedOrders();
    showSnackbar(t('syncing_packed_orders'), 'info');
  }, [syncPackedOrders, showSnackbar, t]);

  const handlefetchOrdersfromAPI = useCallback(() => {
    fetchOrdersfromAPI();
    showSnackbar(t('fetching_orders'), 'info');
  }, [fetchOrdersfromAPI, showSnackbar, t]);

  // Auto-hide when order is selected
  useEffect(() => {
    if (selectedOrderId) {
      setIsListOpen(false);
    }
    else {
      setIsListOpen(true);
    }
  }, [selectedOrderId]);

  return (
    <Box sx={{ position: 'relative' }}>
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Button sx={{ mr: 1 }} 
              color="info"
              onClick={handleFetchOrders}
              variant="contained">
              <RefreshRounded />
            </Button>
            <Button sx={{ mr: 1 }} 
              color="warning"
              onClick={handlefetchOrdersfromAPI}
              variant="contained">
              {t('check_new_orders')}
            </Button>
            <Button
              color="success"
              onClick={handlesyncPackedOrders}
              variant="contained">
              {t('sync_packed_orders')}
            </Button>
          </Paper>
        </Grid>
      </Grid>
      <Grid container spacing={2}>
        {isListOpen && (
          <Grid item xs={3}> {/* When visible, takes 3 columns */}
            <Paper sx={{
              p: 2,
              height: '75vh',
              overflow: 'auto',
            }}>
              <OrdersList />
            </Paper>
          </Grid>
        )}
        <Grid item xs={isListOpen ? 4 : 4}>
          <Paper sx={{ p: 2, height: '75vh', overflow: 'auto' }}>
            <OrderDetail />
          </Paper>
        </Grid>
        <Grid item xs={isListOpen ? 5 : 8}>
          <Paper sx={{ p: 2, height: '75vh', overflow: 'auto' }}>
            <OrderItems showSnackbar={showSnackbar}/>
          </Paper>
        </Grid>
        <Snackbar 
          open={isSnackbarOpen} 
          autoHideDuration={6000} 
          onClose={handleSnackbarClose}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleSnackbarClose} 
            severity={snackbarSeverity} 
            sx={{ 
              minWidth: 300, // Ensure a minimum width for larger appearance
              fontSize: '1.2rem', // Bigger font size
              padding: '16px 24px', // Increase padding for a larger alert box
              display: 'flex', // Ensure flex for centering content
              alignItems: 'center', // Center content vertically
              justifyContent: 'center', // Center content horizontally
              textAlign: 'center' // Ensure text aligns centrally
            }} 
          >
            {snackbarMessage}
          </Alert>
        </Snackbar>
      </Grid>

      <ToggleButton>
        <IconButton 
          onClick={() => setIsListOpen(!isListOpen)}
          sx={{ p: 1 }}
        >
          {isListOpen ? <ChevronLeftIcon /> : <ListIcon />}
        </IconButton>
      </ToggleButton>
    </Box>
  );
};
