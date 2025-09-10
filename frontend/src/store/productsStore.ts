import { create } from 'zustand';
import { productsApi } from '../services/api';
import { Product, ProductVariant, ProductStockAdjustment } from '../types/products';

export type StockAdjustment = ProductStockAdjustment & {
  title?: string;
  variant_code?: string;
  product_code?: string;
};

interface ProductsStore {
  products: Product[];
  variants: ProductVariant[];
  pendingAdjustments: StockAdjustment[];
  isLoading: boolean;
  error: string | null;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  fetchProducts: () => Promise<void>;
  fetchVariants: () => Promise<void>;
  fetchPendingAdjustments: () => Promise<void>;
  fetchAllData: () => Promise<void>;
  addStockAdjustmentEAN: (ean: string, quantity: number) => Promise<void>;
  addStockAdjustmentCode: (code: string, quantity: number) => Promise<void>;
  changeAdjustment: (id: number, quantity: number) => Promise<void>;
  handleDeleteAdj: (id: number) => Promise<void>;
  syncStockAdjustments: () => Promise<void>;
}

export const useProductsStore = create<ProductsStore>((set, get) => ({
  products: [],
  variants: [],
  pendingAdjustments: [],
  isLoading: false,
  error: null,
  searchTerm: '',
  
  setSearchTerm: (term) => set({ searchTerm: term }),
  
  fetchProducts: async () => {
    try {
      const { data } = await productsApi.getProducts();
      set({ products: data });
    } catch (error) {
      set({ error: 'Failed to fetch products' });
    }
  },

  fetchVariants: async () => {
    try {
      const { data } = await productsApi.getVariants();
      set({ variants: data });
    } catch (error) {
      set({ error: 'Failed to fetch variants' });
    }
  },

  fetchPendingAdjustments: async () => {
    try {
      const { data } = await productsApi.getPendingAdjustments();
      const products = get().products;
      
      const enrichedAdjustments = data.map((adj: StockAdjustment) => {
        // Handle both cases where variant can be an ID or object
        const variant = adj.variant ? adj.variant : undefined;
        const product = adj.product ? adj.product : products.find(p => p.id === adj.variant?.product);
        
        return {
          ...adj,
          //variant,
          product,
          image_url: variant?.image_url || product?.image_url || undefined,
          title: product?.title || "",
          variant_code: variant?.code,
          product_code: product?.code
        };
      });
      set({ pendingAdjustments: enrichedAdjustments });
    } catch (error) {
      set({ error: 'Failed to fetch adjustments' });
      console.error('Error in fetchPendingAdjustments:', error);
    }
  },

  fetchAllData: async () => {
    set({ isLoading: true, error: null });
    try {
      // Fetch products and variants first, in parallel
      await Promise.all([
        get().fetchProducts(),
        get().fetchVariants()
      ]);
      // Then fetch adjustments after we have products and variants
      await get().fetchPendingAdjustments();
    } catch (error) {
      console.error('Error in fetchAllData:', error);
      set({ error: 'Failed to fetch all data' });
    } finally {
      set({ isLoading: false });
    }
  },
  addStockAdjustmentEAN: async (ean, quantity?) => {
    const variant = get().variants.find(v => v.ean === ean);
    if (!variant) {
      set({ error: 'Product variant not found' });
      return;
    }

    try {
      await productsApi.addStockAdjustmentVariant({
        variant_code: variant.code,
        adjustment_quantity: quantity || 1
      });
      await get().fetchPendingAdjustments();
    } catch (error) {
      set({ error: 'Failed to add adjustment' });
    }
  },
  addStockAdjustmentCode: async (code, quantity) => {
    const product = get().products.find(p => p.code === code);
    const variant = get().variants.find(v => v.code === code);
    if (variant) {
        // If a variant with the code exists, use it
        try {
            await productsApi.addStockAdjustmentVariant({
                variant_code: variant.code,
                adjustment_quantity: quantity || 1
            });
            await get().fetchPendingAdjustments();
            } catch (error) {
            set({ error: 'Failed to add adjustment' });
        }
        return;
    }    
    if (product) {
      try {
        await productsApi.addStockAdjustmentProduct({
          product_code: product.code,
          adjustment_quantity: quantity || 1
        });
        await get().fetchPendingAdjustments();
      } catch (error) {
        set({ error: 'Failed to add adjustment' });
      }
    }
    else {
      set({ error: 'Product or variant not found' });
    }
    },
  changeAdjustment: async (id, quantity) => {
    const item = get().pendingAdjustments.find(v => v.id === id);
    if (!item) {
      set({ error: 'Product variant not found' });
      return;
    }

    if (item.variant) {

        try {
        await productsApi.addStockAdjustmentVariant({
            variant_code: item.variant.code,
            adjustment_quantity: quantity
        });
        await get().fetchPendingAdjustments();
        } catch (error) {
        set({ error: 'Failed to add adjustment' });
        }
    }
    else if (item.product) {
        try {
        await productsApi.addStockAdjustmentProduct({
            product_code: item.product.code,
            adjustment_quantity: quantity
        });
        await get().fetchPendingAdjustments();
        } catch (error) {
        set({ error: 'Failed to add adjustment' });
        }
    }
    else {
        set({ error: 'Product or variant not found in adjustment' });
    }
  },
    handleDeleteAdj: async (id) => {
        try {
        await productsApi.deleteStockAdjustment(id);
        await get().fetchPendingAdjustments();
        } catch (error) {
        set({ error: 'Failed to delete adjustment' });
        }
    },
    syncStockAdjustments: async () => {
        try {
        await productsApi.syncStockAdjustments();
        // Optionally, you might want to refetch adjustments after syncing
        await get().fetchPendingAdjustments();
        } catch (error) {
        set({ error: 'Failed to sync stock adjustments' });
        }
    },
}));
