export interface Product {
    id: number;
    code: string;
    product_id: number | null;
    title: string | null;
    manufacturer: string | null;
    ean: string | null;
    code_supplier: string | null;
    availability_id: number | null;
    availability: string | null;
    stock: number;
    stock_position: string | null;
    weight: number | null;
    unit: string | null;
    image_url: string | null;
    uma_is_active: boolean;
    uma_last_synced_at: string;
    variants: ProductVariant[];
}

export interface ProductVariant {
    id: number;
    code: string;
    product_id: number;
    variant_id: number | null;
    code_supplier: string | null;
    ean: string | null;
    availability_id: number | null;
    availability: string | null;
    stock: number;
    stock_position: string | null;
    weight: number | null;
    image_url: string | null;
    price_original: number | null;
    price_with_vat: number | null;
    price_without_vat: number | null;
    price_purchase: number | null;
    currency: string | null;
    parameters: Record<string, string> | null;
    uma_is_active: boolean;
    uma_last_synced_at: string;
    product: number | null;
}

export type StockAdjustmentStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

export interface ProductStockAdjustment {
    id: number;
    product?: Product;
    variant?: ProductVariant;
    adjustment_quantity: number;
    status: StockAdjustmentStatus;
    created_at: string;
    processed_at: string | null;
    processed_by: {
        id: number;
        username: string;
    } | null;
    api_response_data: any | null;
    error_message: string | null;
}
