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
  
  // System fields
  status: 'pending' | 'completed';
  created_at: string;
  updated_at: string;
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
  status?: 'pending' | 'completed';
}

export type FilterStatus = 'all' | 'pending' | 'completed';
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
  sort_by?: SortField;
  sort_order?: SortDirection;
}
