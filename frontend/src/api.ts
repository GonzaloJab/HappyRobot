import { Shipment, ShipmentCreate, ShipmentUpdate, ShipmentFilters } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
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
};
