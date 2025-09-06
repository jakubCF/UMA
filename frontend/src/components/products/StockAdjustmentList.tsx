import { List, ListItem, Typography, Box, CircularProgress, CardMedia, Grid, IconButton, Button} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever'
import { useTranslation } from 'react-i18next';
import { useProductsStore, StockAdjustment } from '../../store/productsStore';
import { useEffect, useState } from 'react';


// Interface for the showSnackbar prop that this component expects
interface ProductPageProps {
  showSnackbar: (message: string, severity: 'success' | 'info' | 'error' | 'warning') => void;
}

export const StockAdjustmentList: React.FC<ProductPageProps> = ({ showSnackbar }) => {
  const { t } = useTranslation();
  const { pendingAdjustments, isLoading, error, fetchPendingAdjustments, changeAdjustment, handleDeleteAdj } = useProductsStore();
  const [quantities, setQuantities] = useState<{ [key: string]: number }>({});

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
    const quantity = quantities[adjustment.id];
    changeAdjustment(adjustment.id, quantity);
    // Reset quantity after adjustment
    setQuantities(prev => ({ ...prev, [adjustment.id]: 1 }));
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
      <Typography variant="h6" gutterBottom>
        {t('pending_adjustments')}
      </Typography>
      <List>
        {pendingAdjustments.map((adjustment) => (
          <ListItem key={adjustment.id}>
            <Box>
              <Typography variant="body1">
                {adjustment.product_code || adjustment.variant_code}
              </Typography>
              <Box>
                <Grid container spacing={2}>
                    <Grid item xs={2} sm={2}>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                        <CardMedia
                            component="img"
                            sx={{ 
                            height: '100%',
                            maxHeight: 100, 
                            objectFit: 'contain',
                            margin: 'auto'
                            }}
                            image={adjustment.variant?.image_url || adjustment.product?.image_url || ''}
                            alt={adjustment.title || ''}
                        />
                        </Box>
                    </Grid>
                    <Grid item xs={7} sm={7}>
                        <Typography variant="body2">
                        {adjustment.product_code || adjustment.variant_code} - {adjustment.title}
                        </Typography>
                        <Typography variant="body2">
                        {t('adjustment_quantity')}: {adjustment.adjustment_quantity > 0 ? '+' : ''}{adjustment.adjustment_quantity}
                        </Typography>
                    </Grid>
                    <Grid item xs={3} sm={3}>
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
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Button
                                variant="contained"
                                size="small"
                                
                                onClick={() => handleAdjustment(adjustment)}
                            >
                                {t('update')}
                            </Button>
                            <Button
                                variant="contained"
                                color='error'
                                size="small" onClick={() => handleDelete(adjustment.id)}>
                                <DeleteForeverIcon />
                            </Button>
                        </Box>
                    </Grid>
                </Grid>
              </Box>
            </Box>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};
