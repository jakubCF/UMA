import { create } from 'zustand';
import { Order, OrderStatus, PickStatus} from '../types/orders';
import { ordersApi } from '../services/api';

// Define polling constants
const POLLING_INTERVAL = 5000; // Poll every 5 seconds
const MAX_POLLING_ATTEMPTS = 12; // Max 12 attempts (1 minute total polling time)

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
  pickedQuantities: Record<number, number>;
  setPickedQuantity: (itemId: number, quantity: number) => void; 
  updateItemPicked: (orderId: number, itemId: number, pickedQty: number) => Promise<void>;
  updateOrderStatus: (orderId: number, status?: OrderStatus, itemsToUpdate?: Array<{id: number, uma_picked: PickStatus}>) => Promise<void>;
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
  pickedQuantities: {},
  setPickedQuantity: (itemId, quantity) => {
    set(state => ({
      pickedQuantities: {
        ...state.pickedQuantities,
        [itemId]: quantity,
      },
    }));
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
  updateOrderStatus: async (orderId: number, status: OrderStatus = 'packed', itemsToUpdate) => {
    try {
      await ordersApi.updateOrderStatus(orderId, {uma_status: status, items: itemsToUpdate || ["aaaa"]});
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
      await get().fetchOrders();
      set({ isLoading: false});
    }
    catch (error) {
      set({ error: 'Failed to sync orders', isLoading: false });
    }
  },
  syncPackedOrders: async () => {
    // send POST request to sync orders status from API
    set({ isLoading: true, error: null });
    let  orderIdsToSync: number[] = [];
    const initialStatus = 'packed';
    try {
      const currentOrders = get().orders; // Use current state for IDs to sync
      orderIdsToSync = currentOrders
        .filter((order: Order) => order.uma_status === initialStatus)
        .map((order: Order) => order.id);

      if (orderIdsToSync.length === 0) {
        set({ isLoading: false, error: 'No packed orders to sync.' });
        return;
      }
      // 2. Send POST request to backend to initiate Celery task
      await ordersApi.syncPackedOrders(orderIdsToSync);

      // 3. Start Polling for status updates
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        console.log(`Polling for order status updates... Attempt ${attempts}`);

        try {
          await get().fetchOrders(); // Re-fetch all orders to check their statuses
          const updatedOrders = get().orders;

          // Check if all originally synced orders have changed their status
          const allSynced = orderIdsToSync.every(id => {
            const order = updatedOrders.find(o => o.id === id);
            // Assuming 'completed' is the final status after syncing
            return order && order.uma_status !== initialStatus; 
          });

          if (allSynced) {
            clearInterval(pollInterval);
            set({ isLoading: false, error: null });
            console.log('All packed orders successfully synced and updated.');
          } else if (attempts >= MAX_POLLING_ATTEMPTS) {
            clearInterval(pollInterval);
            set({ isLoading: false, error: 'Timed out waiting for orders to sync.' });
            console.error('Polling timed out.');
          }
        } catch (pollError) {
          console.error('Error during polling:', pollError);
          // Don't stop polling on a single fetch error, but log it
          if (attempts >= MAX_POLLING_ATTEMPTS) {
            clearInterval(pollInterval);
            set({ isLoading: false, error: 'Failed to sync orders due to repeated errors.' });
          }
        }
      }, POLLING_INTERVAL);

    } catch (error) {
      set({ error: 'Failed to initiate order sync or handle polling.', isLoading: false });
      console.error('Error in syncPackedOrders:', error);
    }
  }
}));
