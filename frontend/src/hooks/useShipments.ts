import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';
import { Shipment, ShipmentUpdate, ShipmentFilters } from '../types';

// Query keys
const QUERY_KEYS = {
  shipments: (filters: ShipmentFilters) => ['shipments', filters] as const,
};

// Get all shipments with filters
export function useShipments(filters: ShipmentFilters = {}) {
  return useQuery({
    queryKey: QUERY_KEYS.shipments(filters),
    queryFn: () => api.getShipments(filters),
  });
}

// Create shipment mutation
export function useCreateShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.createShipment,
    onSuccess: () => {
      // Invalidate and refetch all shipments queries
      queryClient.invalidateQueries({ queryKey: ['shipments'] });
    },
  });
}

// Update shipment mutation
export function useUpdateShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ShipmentUpdate }) =>
      api.updateShipment(id, data),
    onSuccess: () => {
      // Invalidate and refetch all shipments queries
      queryClient.invalidateQueries({ queryKey: ['shipments'] });
    },
  });
}

// Delete shipment mutation
export function useDeleteShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.deleteShipment,
    onSuccess: () => {
      // Invalidate and refetch all shipments queries
      queryClient.invalidateQueries({ queryKey: ['shipments'] });
    },
  });
}

// Toggle shipment status (optimistic update)
export function useToggleShipmentStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: 'pending' | 'agreed' }) =>
      api.updateShipment(id, { status }),
    onMutate: async ({ id, status }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['shipments'] });

      // Get all shipments queries and update them optimistically
      const queries = queryClient.getQueriesData({ queryKey: ['shipments'] });
      
      const previousData: Array<{ queryKey: any; data: any }> = [];
      
      queries.forEach(([queryKey, data]) => {
        if (data && Array.isArray(data)) {
          previousData.push({ queryKey, data });
          const updatedData = (data as Shipment[]).map((shipment) =>
            shipment.id === id ? { ...shipment, status } : shipment
          );
          queryClient.setQueryData(queryKey, updatedData);
        }
      });

      return { previousData };
    },
    onError: (_, __, context) => {
      // If the mutation fails, roll back all queries
      if (context?.previousData) {
        context.previousData.forEach(({ queryKey, data }) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['shipments'] });
    },
  });
}
