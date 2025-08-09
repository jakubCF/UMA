import { Grid, Paper, IconButton, Box } from '@mui/material';
import { useState, useEffect } from 'react';
import { styled } from '@mui/material/styles';
import ListIcon from '@mui/icons-material/List';
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

const fetchOrdersfromAPI = () => {
  const { fetchOrdersfromAPI } = useOrdersStore.getState();
  fetchOrdersfromAPI();
};
const syncPackedOrders = () => {
  const { syncPackedOrders } = useOrdersStore.getState();
  syncPackedOrders();
};

export const OrdersPage = () => {
  const { t } = useTranslation();
  const { selectedOrderId } = useOrdersStore();
  const [isListOpen, setIsListOpen] = useState(true);

  // Auto-hide when order is selected
  useEffect(() => {
    if (selectedOrderId) {
      setIsListOpen(false);
    }
  }, [selectedOrderId]);

  return (
    <Box sx={{ position: 'relative' }}>
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Button sx={{ mr: 1 }} 
              color="warning"
              onClick={fetchOrdersfromAPI}
              variant="contained">
              {t('check_new_orders')}
            </Button>
            <Button
              color="success"
              onClick={syncPackedOrders}
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
            <OrderItems />
          </Paper>
        </Grid>
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
