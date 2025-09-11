export interface Shipment {
  id: string;
  // Core/Ops fields
  load_id: string;
  origin: string;
  destination: string;
  pickup_datetime: string;
  delivery_datetime: string;
  
  // Optional core fields
  equipment_type?: string;
  loadboard_rate?: number;
  notes?: string;
  weight?: number;
  commodity_type?: string;
  
  // Dashboard/KPI fields
  num_of_pieces?: number;
  miles?: number;
  dimensions?: string;
  
  // Agreed/Completed fields
  agreed_price?: number;
  carrier_description?: string;
  
  // System fields
  status: 'pending' | 'agreed';
  created_at: string;
  updated_at: string;
  
  // Assignment tracking fields
  assigned_via_url: boolean;
  time_per_call_seconds?: number;
  avg_time_per_call_seconds?: number;
}

export interface ShipmentCreate {
  // Required fields
  load_id: string;
  origin: string;
  destination: string;
  pickup_datetime: string;
  delivery_datetime: string;
  
  // Optional fields
  equipment_type?: string;
  loadboard_rate?: number;
  notes?: string;
  weight?: number;
  commodity_type?: string;
  num_of_pieces?: number;
  miles?: number;
  dimensions?: string;
  agreed_price?: number;
  carrier_description?: string;
}

export interface ShipmentUpdate {
  load_id?: string;
  origin?: string;
  destination?: string;
  pickup_datetime?: string;
  delivery_datetime?: string;
  equipment_type?: string;
  loadboard_rate?: number;
  notes?: string;
  weight?: number;
  commodity_type?: string;
  num_of_pieces?: number;
  miles?: number;
  dimensions?: string;
  status?: 'pending' | 'agreed';
  agreed_price?: number;
  carrier_description?: string;
  time_per_call_seconds?: number;
}

export type FilterStatus = 'all' | 'pending' | 'agreed';
export type SortField = 'created_at' | 'pickup_datetime' | 'delivery_datetime' | 'loadboard_rate' | 'miles';
export type SortDirection = 'asc' | 'desc';

export interface ShipmentFilters {
  status?: FilterStatus;
  equipment_type?: string;
  commodity_type?: string;
  origin?: string;
  destination?: string;
  pickup_from?: string;
  pickup_to?: string;
  delivery_from?: string;
  delivery_to?: string;
  q?: string;
  assigned_via_url?: boolean;
  sort_by?: SortField;
  sort_order?: SortDirection;
}

export interface AssignmentStats {
  count: number;
  total_agreed_price: number;
  total_agreed_minus_loadboard: number;
  avg_time_per_call_seconds: number;
}

export interface ShipmentStats {
  manual: AssignmentStats;
  url_api: AssignmentStats;
}
