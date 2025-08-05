import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',  // adjust to match your Django backend URL
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable CORS credentials
});

// Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 403) {
      console.error('CORS Error:', error);
      // You might want to show a user-friendly message here
    }
    return Promise.reject(error);
  }
);

export const ordersApi = {
  getOrders: () => api.get('/orders/'),
  updateOrderStatus: (orderId: number,  data: { uma_status: string}) => 
    api.patch(`/orders/${orderId}/`, data),
  updateOrderItemStatus: (orderId: number, itemId: number, data: { uma_picked: string }) => 
    api.patch(`/orders/${orderId}/items/${itemId}/status/`, data),
  syncOrdersTask: () => api.post('/sync/', {"type": "orders"}),
  syncPackedOrders: () => api.post('/sync/', {"type": "orders_status", "orderids":[], "statusid": 21, }),
};

export default api;
