import { useEffect } from 'react';
import { List, ListItem, ListItemButton, ListItemText, Typography, CircularProgress, Alert, Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { useOrdersStore } from '../../store/ordersStore';
import { useTranslation } from 'react-i18next';

const OrdersList = () => {
  const { t } = useTranslation();
  const { filteredOrders, selectedOrderId, setSelectedOrderId, isLoading, error, fetchOrders, filterStatus, setFilterStatus } = useOrdersStore();

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  if (isLoading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">{t('orders')}</Typography>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={filterStatus}
            label="Status"
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <MenuItem value="processing">{t('processing')}</MenuItem>
            <MenuItem value="packed">{t('packed')}</MenuItem>
            <MenuItem value="completed">{t('completed')}</MenuItem>
            <MenuItem value="cancelled">{t('cancelled')}</MenuItem>
            <MenuItem value="">{t('all')}</MenuItem>
          </Select>
        </FormControl>
      </Box>
      <List>
        {filteredOrders().map((order) => (
          <ListItem key={order.id} disablePadding>
            <ListItemButton 
              selected={selectedOrderId === order.id}
              onClick={() => setSelectedOrderId(order.id)}
            >
              <ListItemText 
                primary={t('order') + ` ${order.order_number}`}
                secondary={t('delivery:') + ` ${order.shipment?.name || 'No delivery method'}`}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </>
  );
};

export default OrdersList;
