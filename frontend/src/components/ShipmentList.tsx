import { Shipment, FilterStatus, SortField, SortDirection } from '../types';
import { ShipmentItem } from './ShipmentItem';
import { Package } from 'lucide-react';

interface ShipmentListProps {
  shipments: Shipment[];
  searchQuery: string;
  statusFilter: FilterStatus;
  sortField: SortField;
  sortDirection: SortDirection;
  onToggleStatus: (id: string, status: 'pending' | 'completed') => void;
  onEdit: (shipment: Shipment) => void;
  onDelete: (id: string) => void;
}

export function ShipmentList({
  shipments,
  searchQuery,
  statusFilter,
  sortField,
  sortDirection,
  onToggleStatus,
  onEdit,
  onDelete,
}: ShipmentListProps) {
  // Filter shipments
  const filteredShipments = shipments.filter((shipment) => {
    // Status filter
    if (statusFilter !== 'all' && shipment.status !== statusFilter) {
      return false;
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const matchesTitle = shipment.title.toLowerCase().includes(query);
      const matchesDestination = shipment.destination?.toLowerCase().includes(query) || false;
      if (!matchesTitle && !matchesDestination) {
        return false;
      }
    }

    return true;
  });

  // Sort shipments
  const sortedShipments = [...filteredShipments].sort((a, b) => {
    let aValue: any;
    let bValue: any;

    switch (sortField) {
      case 'title':
        aValue = a.title.toLowerCase();
        bValue = b.title.toLowerCase();
        break;
      case 'eta':
        aValue = a.eta ? new Date(a.eta).getTime() : 0;
        bValue = b.eta ? new Date(b.eta).getTime() : 0;
        break;
      case 'created_at':
      default:
        aValue = new Date(a.created_at).getTime();
        bValue = new Date(b.created_at).getTime();
        break;
    }

    if (sortDirection === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    }
  });

  if (sortedShipments.length === 0) {
    return (
      <div className="text-center py-12">
        <Package className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No shipments found</h3>
        <p className="mt-1 text-sm text-gray-500">
          {searchQuery || statusFilter !== 'all'
            ? 'Try adjusting your search or filter criteria.'
            : 'Get started by creating a new shipment.'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {sortedShipments.map((shipment) => (
        <ShipmentItem
          key={shipment.id}
          shipment={shipment}
          onToggleStatus={onToggleStatus}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
