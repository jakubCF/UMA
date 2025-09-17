import { Grid, Box, Snackbar, Alert, Paper, Button } from '@mui/material';
import { useEffect, useRef, useState, useCallback } from 'react';
import { ProductSearch } from '../components/products/ProductSearch';
import { StockAdjustmentList } from '../components/products/StockAdjustmentList';
import { useProductsStore } from '../store/productsStore';
import { useTranslation } from 'react-i18next';

export const ProductsPage = () => {
  const { t } = useTranslation();
  const barcodeBuffer = useRef('');
  const barcodeTimeout = useRef<NodeJS.Timeout>();
  const { addStockAdjustmentEAN, fetchAllData, syncStockAdjustments } = useProductsStore();

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

    const handleSyncStockAdjustments = useCallback(() => {
      syncStockAdjustments();
      showSnackbar(t('syncing_stock_adjustments'), 'info');
      (document.activeElement as HTMLElement)?.blur();
    }, [syncStockAdjustments, showSnackbar, t]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  useEffect(() => {
    const handleKeyPress = async (event: KeyboardEvent) => {
      if (event.key === 'Enter' && barcodeBuffer.current) {
        const response = await addStockAdjustmentEAN(barcodeBuffer.current, 1);
        if (response.success) {
          showSnackbar(t('adjustment_added') + ' EAN: ' + barcodeBuffer.current, 'success');
        } else {
          showSnackbar(response.message + ' EAN: ' + barcodeBuffer.current, 'error');
        }
        barcodeBuffer.current = '';
        return;
      }

      // Reset timeout
      if (barcodeTimeout.current) {
        clearTimeout(barcodeTimeout.current);
      }

      // Accumulate barcode
      barcodeBuffer.current += event.key;

      // Clear buffer after delay
      barcodeTimeout.current = setTimeout(() => {
        barcodeBuffer.current = '';
      }, 100);
    };

    window.addEventListener('keypress', handleKeyPress);
    return () => window.removeEventListener('keypress', handleKeyPress);
  }, [addStockAdjustmentEAN, showSnackbar, t]);

  return (
    <Box>
       <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Button
              color="success"
              onClick={handleSyncStockAdjustments}
              variant="contained"
              onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
              }
              }}>
              {t('update_stock_levels')}
            </Button>
          </Paper>
        </Grid>
      </Grid>
      <Grid container spacing={2}>
        <Grid item xs={6}>
            <ProductSearch showSnackbar={showSnackbar}/>
        </Grid>
        <Grid item xs={6}>
          <Paper sx={{ p: 2, height: '77vh', overflow: 'auto' }}>
            <StockAdjustmentList showSnackbar={showSnackbar}/>
          </Paper>
        </Grid>
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
    </Box>
  );
};
