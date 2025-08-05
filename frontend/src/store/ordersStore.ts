import { create } from 'zustand';
import { Order, OrderStatus } from '../types/orders';
import { ordersApi } from '../services/api';

interface OrdersState {
  orders: Order[];
  selectedOrderId: number | null;
  isLoading: boolean;
  error: string | null;
  fetchOrders: () => Promise<void>;
  setOrders: (orders: Order[]) => void;
  setSelectedOrderId: (id: number | null) => void;
  filterStatus: string;
  setFilterStatus: (status: string) => void;
  selectedOrder: () => Order | undefined;
  filteredOrders: () => Order[];
  updateItemPicked: (orderId: number, itemId: number, pickedQty: number) => Promise<void>;
  updateOrderStatus: (orderId: number, status?: OrderStatus) => Promise<void>;
  fetchOrdersfromAPI: () => Promise<void>;
  syncPackedOrders: () => Promise<void>;
}

export const useOrdersStore = create<OrdersState>((set, get) => ({
  orders: [],
  selectedOrderId: null,
  isLoading: false,
  error: null,
  filterStatus: 'processing',
  fetchOrders: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await ordersApi.getOrders();
      set({ orders: response.data, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch orders', isLoading: false });
    }
  },
  setOrders: (orders) => set({ 
      orders: orders.sort((a, b) => {
          const numA = parseInt(a.order_number.slice(1), 10);
          const numB = parseInt(b.order_number.slice(1), 10);
          return numA - numB;
      }) 
  }),
  setSelectedOrderId: (id) => set({ selectedOrderId: id }),
  setFilterStatus: (status) => set({ filterStatus: status }),
  filteredOrders: () => {
    const { orders, filterStatus } = get();
    if (!filterStatus) return orders;
    return orders.filter(order => order.uma_status === filterStatus).sort((a, b) => {
                  const numA = parseInt(a.order_number.slice(1), 10);
                  const numB = parseInt(b.order_number.slice(1), 10);

                  return numA - numB;});
  },
  selectedOrder: () => {
    const { selectedOrderId, orders } = get();
    return orders.find(o => o.id === selectedOrderId);
  },
  updateItemPicked: async (orderId: number, itemId: number, pickedQty: number) => {
    const order = get().orders.find(o => o.id === orderId);
    if (!order) return;

    const item = order.items.find(i => i.id === itemId);
    if (!item) return;

    // Validate and clamp the picked quantity
    const itemQuantity = Number(item.quantity);
    const validatedQty = Math.max(0, Math.min(pickedQty, itemQuantity));
    
    const status = (validatedQty === 0 ? 'not_picked' :
                   validatedQty === itemQuantity ? 'picked' : 
                   'partially_picked') as Order['items'][0]['uma_picked'];
    
    try {
      // Update local state first for immediate feedback
      const updatedOrders = get().orders.map(o => {
        if (o.id === orderId) {
          return {
            ...o,
            items: o.items.map(i => {
              if (i.id === itemId) {
                return { ...i, uma_picked: status };
              }
              return i;
            })
          };
        }
        return o;
      });
      set({ orders: updatedOrders });

      // Then update backend
      await ordersApi.updateOrderItemStatus(order.id, itemId, { uma_picked: status });
    } catch (error) {
      set({ error: 'Failed to update item status' });
    }
  },
  updateOrderStatus: async (orderId: number, status: OrderStatus = 'packed') => {
    try {
      await ordersApi.updateOrderStatus(orderId, {uma_status: status});
      // Optionally, you can refetch orders or update state to reflect the change
      const updatedOrders = get().orders.map(o => {
        if (o.id === orderId) {
          return { ...o, uma_status: status };
        }
        return o;
      });
      set({ orders: updatedOrders });
    } catch (error) {
      set({ error: 'Failed to complete order' });
    }
  },
  fetchOrdersfromAPI: async () => {
    // send POST request to sync orders from API
    set({ isLoading: true, error: null });
    try {
      await ordersApi.syncOrdersTask();
      const response = await ordersApi.getOrders();
      set({ isLoading: false});
    }
    catch (error) {
      set({ error: 'Failed to sync orders', isLoading: false });
    }
  },
  syncPackedOrders: async () => {
    // send POST request to sync orders status from API
    set({ isLoading: true, error: null });
    try {
      await ordersApi.syncPackedOrders();
      const response = await ordersApi.getOrders();
      set({ isLoading: false });
    } catch (error) {
      set({ error: 'Failed to sync orders status', isLoading: false });
    }
  }
}));
