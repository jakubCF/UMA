import { Typography, Box, CircularProgress, CardMedia, Grid, IconButton, Button, Card, CardContent, Dialog, DialogTitle, DialogContent, DialogActions, Divider, Paper } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever'
import CloseIcon from '@mui/icons-material/Close';
import { useTranslation } from 'react-i18next';
import { useProductsStore, StockAdjustment } from '../../store/productsStore';
import { useEffect, useState } from 'react';


// Interface for the showSnackbar prop that this component expects
interface ProductPageProps {
  showSnackbar: (message: string, severity: 'success' | 'info' | 'error' | 'warning') => void;
}

// Helper function to format each parameter string
const formatParameterString = (key: string, value: any) => {
  if (typeof value === 'object' && value !== null) {
    return `${value.name || key}: ${value.value || JSON.stringify(value)}`;
  }
  return `${key}: ${value}`;
};

export const StockAdjustmentList: React.FC<ProductPageProps> = ({ showSnackbar }) => {
  const { t } = useTranslation();
  const { pendingAdjustments, isLoading, error, fetchPendingAdjustments, changeAdjustment, handleDeleteAdj } = useProductsStore();
  const [quantities, setQuantities] = useState<{ [key: string]: number }>({});
  const [openDialog, setOpenDialog] = useState(false);

  // Calculate summary of products by parent code
  const getProductSummary = () => {
    const summary: { [key: string]: number } = {};
    
    pendingAdjustments.forEach(adjustment => {
      const code = adjustment.variant_code || adjustment.product_code || '';
      const parentCode = code.split('-')[0];
      summary[parentCode] = (summary[parentCode] || 0) + adjustment.adjustment_quantity;
    });

    return summary;
  };

  useEffect(() => {
    fetchPendingAdjustments();
  }, [fetchPendingAdjustments]);

  const handleQuantityChange = (variantId: number, value: number) => {
    setQuantities(prev => ({
      ...prev,
      [variantId]: value
    }));
  };

  const handleAdjustment = (adjustment: StockAdjustment) => {
    const quantity = quantities[adjustment.id] || 0;
    // Prevent adjustment if quantity is 0
    if (quantity === 0) {
      showSnackbar(t('quantity_cannot_be_zero'), 'error');
      return;
    }
    changeAdjustment(adjustment.id, quantity);
    // Reset quantity after adjustment
    setQuantities(prev => ({ ...prev, [adjustment.id]: 0 }));
    showSnackbar( t('adjustment_changed') + ' code: ' + adjustment.variant_code , 'success');
  };

  const handleDelete = (id: number) => {
    handleDeleteAdj(id);
    showSnackbar( t('adjustment_deleted') + ' code:' , 'info');
  }

  if (isLoading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          {t('pending_adjustments')}
        </Typography>
        <Button
          variant="outlined"
          size="small"
          onClick={() => setOpenDialog(true)}
        >
          {t('details')}
        </Button>
      </Box>

      <Dialog 
        open={openDialog} 
        onClose={() => setOpenDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          pb: 1
        }}>
          <Typography variant="h6">{t('adjustment_summary')}</Typography>
          <IconButton onClick={() => setOpenDialog(false)} size="small">
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <Divider />
        <DialogContent sx={{ pt: 2 }}>
          <Paper elevation={0} sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
            {Object.entries(getProductSummary()).map(([parentCode, total]) => (
              <Box 
                key={parentCode}
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  py: 1,
                  borderBottom: '1px solid #e0e0e0',
                  '&:last-child': {
                    borderBottom: 'none'
                  }
                }}
              >
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  {parentCode}
                </Typography>
                <Typography 
                  variant="body1"
                  sx={{ 
                    color: total > 0 ? 'success.main' : 'error.main',
                    fontWeight: 500
                  }}
                >
                  {total > 0 ? '+' : ''}{total}
                </Typography>
              </Box>
            ))}
          </Paper>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button 
            onClick={() => setOpenDialog(false)}
            variant="contained"
            size="small"
          >
            {t('close')}
          </Button>
        </DialogActions>
      </Dialog>

      <Grid container spacing={2}>
        {pendingAdjustments.map((adjustment) => (
          <Grid item xs={12} key={adjustment.id}>
            <Card>
              <Grid container>
                <Grid item xs={3} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <CardMedia
                    component="img"
                    sx={{ 
                      height: '100%',
                      maxHeight: 120, 
                      objectFit: 'contain',
                      margin: 'auto'
                    }}
                    image={adjustment.variant?.image_url || adjustment.product?.image_url || ''}
                    alt={adjustment.title || ''}
                  />
                </Grid>
                <Grid item xs={9} sx={{ display: 'flex' }}>
                  <CardContent sx={{ flexGrow: 1, p: 2 }}>
                    <Grid container sx={{ height: '100%' }}>
                      <Grid item xs={7}>
                        <Typography variant="subtitle1">
                          {adjustment.variant_code || adjustment.product_code}
                        </Typography>
                        <Typography variant="body2">{adjustment.title}</Typography>
                        {adjustment.variant?.parameters && Object.entries(adjustment.variant.parameters).map(([key, value]) => (
                          <Typography key={key} variant="body2">
                            {formatParameterString(key, value)}
                          </Typography>
                        ))}
                        <Typography variant="body2" sx={{ mt: 2 }}>
                          {t('adjustment_quantity')}: {adjustment.adjustment_quantity > 0 ? '+' : ''}{adjustment.adjustment_quantity}
                        </Typography>
                      </Grid>
                      <Grid item xs={5}>
                        <Box sx={{ 
                          display: 'flex', 
                          flexDirection: 'column', 
                          alignItems: 'flex-end',
                          height: '100%',
                          gap: 2
                        }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <IconButton size="small" onClick={() => handleQuantityChange(adjustment.id, (quantities[adjustment.id] || 0) - 1)}>
                              <RemoveIcon />
                            </IconButton>
                            <input
                              type="number"
                              style={{ width: 60, textAlign: 'center' }}
                              value={quantities[adjustment.id] || 0}
                              onChange={(e) => handleQuantityChange(adjustment.id, parseInt(e.target.value))}
                            />
                            <IconButton size="small" onClick={() => handleQuantityChange(adjustment.id, (quantities[adjustment.id] || 0) + 1)}>
                              <AddIcon />
                            </IconButton>
                          </Box>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Button
                              variant="contained"
                              size="small"
                              sx={{ minWidth: 90 }}
                              onClick={() => handleAdjustment(adjustment)}
                            >
                              {t('update')}
                            </Button>
                            <Button
                              variant="contained"
                              color='error'
                              size="small"
                              onClick={() => handleDelete(adjustment.id)}
                            >
                              <DeleteForeverIcon />
                            </Button>
                          </Box>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Grid>
              </Grid>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
