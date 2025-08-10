import axios from 'axios';
import { getCsrfToken } from '../utils/csrf';
import dayjs from 'dayjs';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable CORS credentials
});

api.interceptors.request.use(
  (config) => {
    // Only add CSRF token for non-GET requests
    if (config.method && !['get', 'head', 'options'].includes(config.method.toLowerCase())) {
      const csrfToken = getCsrfToken();
      if (csrfToken) {
        // Common headers for CSRF tokens
        // Use 'X-CSRFToken' for Django, 'X-XSRF-TOKEN' for some other frameworks
        // Check your backend's expected header name
        config.headers['X-CSRFToken'] = csrfToken; 
      } else {
        // console.warn('CSRF token not found for non-GET request!');
        // Optionally, you could throw an error or handle it more explicitly
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

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
  syncOrdersTask: () => api.post('/sync/', {"type": "orders", "creation_time_from": dayjs().subtract(14, 'day').format('YYYY-MM-DD')}),
  syncPackedOrders: (orderids:number[]) => api.post('/sync/', {"type": "orders_status", "orderids":orderids, "statusid": 21, }),
};

export default api;
