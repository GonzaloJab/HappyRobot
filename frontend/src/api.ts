import { Shipment, ShipmentCreate, ShipmentUpdate, ShipmentFilters, ShipmentStats, PhoneCall, PhoneCallCreate } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'HapRob-OTVHhErcXLu2eKkUMP6lDtrd8UNi61KZo4FvGALqem0NoJO1uWlz7OywCN0BNoNaG2x5Y';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  // Use /api/ prefix for production, direct URL for development
  const baseUrl = API_BASE_URL.includes('localhost') ? API_BASE_URL : '';
  const apiPrefix = API_BASE_URL.includes('localhost') ? '' : '/api';
  const url = `${baseUrl}${apiPrefix}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText || `HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

function buildQueryString(filters: ShipmentFilters): string {
  const params = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value.toString());
    }
  });
  
  return params.toString();
}

export const api = {
  // Get all shipments with optional filters
  getShipments: (filters: ShipmentFilters = {}): Promise<Shipment[]> => {
    const queryString = buildQueryString(filters);
    const endpoint = queryString ? `/shipments?${queryString}` : '/shipments';
    return fetchApi<Shipment[]>(endpoint);
  },

  // Create a new shipment
  createShipment: (data: ShipmentCreate): Promise<Shipment> =>
    fetchApi<Shipment>('/shipments', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Update a shipment
  updateShipment: (id: string, data: ShipmentUpdate): Promise<Shipment> =>
    fetchApi<Shipment>(`/shipments/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  // Delete a shipment
  deleteShipment: (id: string): Promise<void> =>
    fetchApi<void>(`/shipments/${id}`, {
      method: 'DELETE',
    }),

  // Update a shipment via manual frontend assignment
  updateShipmentManual: (id: string, data: ShipmentUpdate): Promise<Shipment> =>
    fetchApi<Shipment>(`/shipments/${id}/manual`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  // Get shipment statistics
  getShipmentStats: (filters: ShipmentFilters = {}): Promise<ShipmentStats> => {
    const queryString = buildQueryString(filters);
    const endpoint = queryString ? `/shipments/stats?${queryString}` : '/shipments/stats';
    return fetchApi<ShipmentStats>(endpoint);
  },

  // Phone Call methods
  // Add a phone call to a shipment
  addPhoneCall: (shipmentId: string, data: PhoneCallCreate): Promise<PhoneCall> =>
    fetchApi<PhoneCall>(`/shipments/${shipmentId}/phone-calls`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Get all phone calls for a shipment
  getPhoneCalls: (shipmentId: string): Promise<PhoneCall[]> =>
    fetchApi<PhoneCall[]>(`/shipments/${shipmentId}/phone-calls`),

  // Delete all phone calls for a shipment
  deleteAllPhoneCalls: (shipmentId: string): Promise<void> =>
    fetchApi<void>(`/shipments/${shipmentId}/phone-calls`, {
      method: 'DELETE',
    }),

  // Get all phone calls across all shipments
  getAllPhoneCalls: (filters: { call_type?: string; agreed?: boolean; sentiment?: string } = {}): Promise<PhoneCall[]> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
    const queryString = params.toString();
    const endpoint = queryString ? `/phone-calls?${queryString}` : '/phone-calls';
    return fetchApi<PhoneCall[]>(endpoint);
  },
};
