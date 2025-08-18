import React, { useState, useEffect } from 'react';
import { FormControl, InputLabel, Select, MenuItem, Box, Typography, Divider, Button } from '@mui/material';
import { useOrdersStore } from '../../store/ordersStore';
import { OrderStatus} from '../../types/orders';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useTranslation } from 'react-i18next';

const OrderDetail = () => {
  const { t } = useTranslation();
  const { selectedOrder, updateOrderStatus, filteredOrders, setSelectedOrderId, pickedQuantities } = useOrdersStore();
  const [ newStatus, setnewStatus ] = useState<OrderStatus>(selectedOrder()?.uma_status || 'processing');
  const ALL_ORDER_STATUSES = ['processing', 'packed', 'completed', 'cancelled', 'error'];

  const order = selectedOrder();

  useEffect(() => {
    if (order) {
      setnewStatus(order.uma_status);
    } else {
      setnewStatus('processing');
    }
  }, [order]);

  if (!order) {
    return <Typography>{t('select_order_details')}</Typography>;
  }

  const handleCompleteAndLoadNext = () => {
    // 1. Update the order status to 'packed'
    // 2. Fetch and load the next order.
    handleMarkOrderPacked()
      .then(() => {
        // 2. Logic to load the next order
      const filtered = filteredOrders();
      if (filtered.length !== 0){
        setSelectedOrderId(filtered[0].id);
      }
      else {
        setSelectedOrderId(null);
      }
      })
      .catch(error => {
        console.error('Failed to mark order as packed:', error);
      });
  };

  const handleMarkOrderPacked = async () => {

    // Prepare items data to send to backend
    const itemsToUpdate = order.items.map(item => {
      const finalPickedQty = pickedQuantities[item.id] || 0;
      const totalQuantity = Number(item.quantity);

      // Determine the final status based on picked quantity
      let finalUmaPickedStatus: 'not_picked' | 'partially_picked' | 'picked';
      if (finalPickedQty >= totalQuantity) {
        finalUmaPickedStatus = 'picked';
      } else if (finalPickedQty > 0) {
        finalUmaPickedStatus = 'partially_picked';
      } else {
        finalUmaPickedStatus = 'not_picked';
      }

      return {
        id: item.id,
        uma_picked: finalUmaPickedStatus,
      };
    });

    try {
      // Call the store action to update the order status and all item statuses/quantities
      // Assuming updateOrderCompleted can now accept an array of item updates
      await updateOrderStatus(order.id, 'packed', itemsToUpdate); // Pass itemsToUpdate

    } catch (error) {
      console.error('Failed to mark order as completed:', error);
      // Optionally, you can show a user-friendly error message here
    }
  };

  const handleChangeStatus = async () => {
    try {
      await updateOrderStatus(order.id, newStatus);
      // Optionally, you can show a success Snackbar after changing status
      setSelectedOrderId(null); // Refresh the selected order to reflect changes
    } catch (error) {
      console.error('Failed to change order status:', error);
      // Optionally, you can show a user-friendly error message here
    }
  };

  const isOrderProcessing = order.uma_status === "processing"; // Assuming 'order.status' exists

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Order {order.order_number}</Typography>
      <Divider sx={{ my: 2 }} />
      
      <Typography variant="body1" gutterBottom>
        <strong>{t('status')}:</strong> {order.status || 'N/A'}
      </Typography>
      <Typography variant="body1" gutterBottom>
        <strong>{t('delivery_method')}</strong> {order.shipment?.name || 'No delivery method'}
      </Typography>
      <Typography variant="body1" gutterBottom>
        <strong>{t('total_price')}</strong> {order.order_total} CZK
      </Typography>
      <Typography variant="body1" gutterBottom>
        <strong>{t('total_quantity')}</strong> {order.items.reduce((sum, item) => sum + Number(item.quantity), 0.00)}
      </Typography>

      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" color="text.secondary" component="div">
          <strong>{t('customer_note')}</strong>
          <Box sx={{ mt: 1 }}>{order.customer?.customer_note || 'No customer note'}</Box>
        </Typography>
      </Box>
      
      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" color="text.secondary" component="div">
          <strong>{t('internal_note')}</strong>
          <Box sx={{ mt: 1 }}>{order.internal_note || 'No internal note'}</Box>
        </Typography>
      </Box>
      <Box sx={{ mt: 2 }}>
      <Button
          variant="contained"
          color="success"
          onClick={handleCompleteAndLoadNext}
          disabled={!isOrderProcessing} // Disable button if the order is already completed
          startIcon={isOrderProcessing ? null : <CheckCircleIcon />}
          fullWidth
        >
          {isOrderProcessing ? t('mark_packed_load_next') : t('order_completed')}
      </Button>
      <FormControl size="small" sx={{ minWidth: 120, mt: 2, mr: 1 }}>
        <InputLabel>Status</InputLabel>
        <Select
          value={newStatus}
          label="Status"
          onChange={(e) => setnewStatus(e.target.value as OrderStatus)}
        >
          {ALL_ORDER_STATUSES!.map((status) => (
            <MenuItem key={status} value={status}>
              {t(status)}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Button
          variant="outlined"
          color="primary"
          onClick={() => handleChangeStatus()}
          sx={{ mt: 2 }}
        >
          {t('change_status')}
      </Button>
      </Box>
    </Box>
  );
};

export default OrderDetail;
