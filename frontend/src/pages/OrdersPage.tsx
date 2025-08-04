import { Grid, Paper, IconButton, Box } from '@mui/material';
import { useState, useEffect } from 'react';
import { styled } from '@mui/material/styles';
import ListIcon from '@mui/icons-material/List';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { useOrdersStore } from '../store/ordersStore';
import OrdersList from '../components/orders/OrdersList';
import OrderDetail from '../components/orders/OrderDetail';
import OrderItems from '../components/orders/OrderItems';

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
      <Grid container spacing={2}>
        <Grid 
          item 
          sx={{ 
            width: isListOpen ? '25%' : 0,
            transition: 'width 0.3s ease',
            overflow: 'hidden'
          }}
        >
          <Paper sx={{ 
            p: 2, 
            height: '85vh', 
            overflow: 'auto',
            visibility: isListOpen ? 'visible' : 'hidden'
          }}>
            <OrdersList />
          </Paper>
        </Grid>
        <Grid item xs={isListOpen ? 4 : 4}>
          <Paper sx={{ p: 2, height: '85vh', overflow: 'auto' }}>
            <OrderDetail />
          </Paper>
        </Grid>
        <Grid item xs={isListOpen ? 5 : 7}>
          <Paper sx={{ p: 2, height: '85vh', overflow: 'auto' }}>
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
