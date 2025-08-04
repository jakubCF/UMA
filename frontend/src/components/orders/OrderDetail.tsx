import { Box, Typography, Divider, Button } from '@mui/material';
import { useOrdersStore } from '../../store/ordersStore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const OrderDetail = () => {
  const { selectedOrder, updateOrderStatus, filteredOrders, setSelectedOrderId } = useOrdersStore();

  if (!selectedOrder()) {
    return <Typography>Select an order to view details</Typography>;
  }

  const order = selectedOrder()!;

  const handleCompleteAndLoadNext = () => {
    // 1. Update the order status to 'packed'
    // 2. Fetch and load the next order.
    updateOrderStatus(order.id, 'packed')
      .then(() => {
        // 2. Logic to load the next order
      const filtered = filteredOrders();
      if (filtered.length !== 0){
        setSelectedOrderId(filtered[0].id);
      }
      })
      .catch(error => {
        console.error('Failed to mark order as packed:', error);
      });
  };

  const isOrderPacked = order.status === 'packed'; // Assuming 'order.status' exists


  return (
    <Box>
      <Typography variant="h6" gutterBottom>Order {order.order_number}</Typography>
      <Divider sx={{ my: 2 }} />
      
      <Typography variant="body1" gutterBottom>
        <strong>Delivery Method:</strong> {order.shipment?.name || 'No delivery method'}
      </Typography>
      <Typography variant="body1" gutterBottom>
        <strong>Total Price:</strong> {order.order_total} CZK
      </Typography>
      <Typography variant="body1" gutterBottom>
        <strong>Total quantity:</strong> {order.items.reduce((sum, item) => sum + Number(item.quantity), 0.00)}
      </Typography>

      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" color="text.secondary" component="div">
          <strong>Customer Note:</strong>
          <Box sx={{ mt: 1 }}>{order.customer?.customer_note || 'No customer note'}</Box>
        </Typography>
      </Box>
      
      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" color="text.secondary" component="div">
          <strong>Internal Note:</strong>
          <Box sx={{ mt: 1 }}>{order.internal_note || 'No internal note'}</Box>
        </Typography>
      </Box>
      <Box sx={{ mt: 2 }}>
      <Button
          variant="contained"
          color="success"
          onClick={handleCompleteAndLoadNext}
          disabled={isOrderPacked} // Disable button if the order is already completed
          startIcon={isOrderPacked ? <CheckCircleIcon /> : null}
          fullWidth
        >
          {isOrderPacked ? 'Order Packed' : 'Mark as Packed & Load Next'}
        </Button>

      </Box>
    </Box>
  );
};

export default OrderDetail;
