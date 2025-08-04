export type OrderStatus = 'processing' | 'packed' | 'label_pending' | 'label_created' | 'label_printed' | 'completed' | 'cancelled' | 'error';
export type PickStatus = 'not_picked' | 'picked' | 'unavailable';

export interface OrderItem {
  id: number;
  product_id: number | null;
  options_set_id: number | null;
  type: string | null;
  uuid: string | null;
  parent_uuid: string | null;
  code: string | null;
  code_supplier: string | null;
  supplier: string | null;
  ean: string | null;
  title: string | null;
  adult_yn: boolean;
  unit: string | null;
  quantity: number;
  price: number | null;
  weight: number | null;
  availability: string | null;
  stock_position: string | null;
  parameters: Record<string, string> | null;
  image_url: string | null;
  uma_picked: PickStatus;
  uma_created_at: string;
  uma_updated_at: string;
}

export interface Order {
  id: number;
  order_number: string;
  order_id: number;
  case_number: string | null;
  external_order_number: string | null;
  uuid: string | null;
  status_id: number;
  status: string | null;
  paid_date: string | null;
  tracking_code: string | null;
  tracking_url: string | null;
  internal_note: string | null;
  creation_time: string | null;
  order_total: number | null;
  invoice_number: string | null;
  customer: {
    [key: string]: any;
  } | null;
  shipment: {
    [key: string]: any;
  } | null;
  payment: {
    [key: string]: any;
  } | null;
  items: OrderItem[];
  uma_status: OrderStatus;
  uma_created_at: string;
  uma_updated_at: string;
}
