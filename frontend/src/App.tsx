import { useState } from 'react';
import { Plus, Loader2, Package } from 'lucide-react';
import { Shipment, FilterStatus, SortField, SortDirection, ShipmentFilters, PhoneCallCreate } from './types';
import { useShipments, useCreateShipment, useUpdateShipmentManual, useDeleteShipment, useShipmentStats } from './hooks/useShipments';
import { api } from './api';
import { LoadFiltersBar } from './components/LoadFiltersBar';
import { LoadStatsBar } from './components/LoadStatsBar';
import { HeadlineStatsBar } from './components/HeadlineStatsBar';
import { LoadItem } from './components/LoadItem';
import { LoadForm } from './components/LoadForm';
import { DeleteConfirmDialog } from './components/DeleteConfirmDialog';

function App() {
  // State for filters and sorting
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('all');
  const [equipmentTypeFilter, setEquipmentTypeFilter] = useState('');
  const [commodityTypeFilter, setCommodityTypeFilter] = useState('');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // State for modals
  const [isNewFormOpen, setIsNewFormOpen] = useState(false);
  const [editingShipment, setEditingShipment] = useState<Shipment | null>(null);
  const [deletingShipment, setDeletingShipment] = useState<Shipment | null>(null);

  // Build filters object
  const filters: ShipmentFilters = {
    q: searchQuery || undefined,
    status: statusFilter === 'all' ? undefined : statusFilter,
    equipment_type: equipmentTypeFilter || undefined,
    commodity_type: commodityTypeFilter || undefined,
    sort_by: sortField,
    sort_order: sortDirection,
  };

  // Data hooks
  const { data: shipments = [], isLoading, error } = useShipments(filters);
  const { data: stats, isLoading: statsLoading } = useShipmentStats(filters);
  const createShipment = useCreateShipment();
  const updateShipmentManual = useUpdateShipmentManual();
  const deleteShipment = useDeleteShipment();

  // Handlers
  const handleCreateShipment = async (data: any) => {
    try {
      await createShipment.mutateAsync(data);
    } catch (error) {
      console.error('Failed to create load:', error);
    }
  };

  const handleUpdateShipment = async (data: any) => {
    if (!editingShipment) return;
    try {
      // Use manual endpoint for frontend updates
      await updateShipmentManual.mutateAsync({ id: editingShipment.id, data });
    } catch (error) {
      console.error('Failed to update load:', error);
    }
  };

  const handleDeleteShipment = async (id: string) => {
    try {
      await deleteShipment.mutateAsync(id);
    } catch (error) {
      console.error('Failed to delete load:', error);
    }
  };

  const handleAddPhoneCall = async (shipmentId: string, phoneCall: PhoneCallCreate) => {
    try {
      await api.addPhoneCall(shipmentId, phoneCall);
      // Refresh the shipments data to show the new phone call
      window.location.reload(); // Simple refresh for now
    } catch (error) {
      console.error('Failed to add phone call:', error);
    }
  };

  const handleAssignManually = (shipment: Shipment) => {
    setEditingShipment(shipment);
  };

  const handleDelete = (id: string) => {
    const shipment = shipments.find(s => s.id === id);
    if (shipment) {
      setDeletingShipment(shipment);
    }
  };

  const confirmDelete = () => {
    if (deletingShipment) {
      handleDeleteShipment(deletingShipment.id);
      setDeletingShipment(null);
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Loads</h2>
          <p className="text-gray-600 mb-4">
            {error instanceof Error ? error.message : 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="btn btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Loads Manager</h1>
              <p className="mt-1 text-sm text-gray-600">
                Manage your loads and track their status
              </p>
            </div>
            <button
              onClick={() => setIsNewFormOpen(true)}
              className="btn btn-primary flex items-center space-x-2"
            >
              <Plus className="h-4 w-4" />
              <span>New Load</span>
            </button>
          </div>
        </div>

        {/* Headline Stats */}
        {stats && <HeadlineStatsBar stats={stats} isLoading={statsLoading} />}

        {/* Additional Stats */}
        <LoadStatsBar shipments={shipments} />

        {/* Filters */}
        <LoadFiltersBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          statusFilter={statusFilter}
          onStatusFilterChange={setStatusFilter}
          equipmentTypeFilter={equipmentTypeFilter}
          onEquipmentTypeFilterChange={setEquipmentTypeFilter}
          commodityTypeFilter={commodityTypeFilter}
          onCommodityTypeFilterChange={setCommodityTypeFilter}
          sortField={sortField}
          onSortFieldChange={setSortField}
          sortDirection={sortDirection}
          onSortDirectionChange={setSortDirection}
        />

        {/* Content */}
        <div className="mt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
              <span className="ml-2 text-gray-600">Loading loads...</span>
            </div>
          ) : shipments.length === 0 ? (
            <div className="text-center py-12">
              <Package className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No loads found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchQuery || statusFilter !== 'all' || equipmentTypeFilter || commodityTypeFilter
                  ? 'Try adjusting your search or filter criteria.'
                  : 'Get started by creating a new load.'}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {shipments.map((shipment) => (
                <LoadItem
                  key={shipment.id}
                  shipment={shipment}
                  onEdit={handleAssignManually}
                  onDelete={handleDelete}
                  onAddPhoneCall={handleAddPhoneCall}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <LoadForm
        isOpen={isNewFormOpen}
        onClose={() => setIsNewFormOpen(false)}
        onSubmit={handleCreateShipment}
        isLoading={createShipment.isPending}
        title="Create New Load"
      />

      <LoadForm
        isOpen={!!editingShipment}
        onClose={() => setEditingShipment(null)}
        onSubmit={handleUpdateShipment}
        onAddPhoneCall={handleAddPhoneCall}
        isLoading={updateShipmentManual.isPending}
        initialData={editingShipment || undefined}
        title="Edit Load"
      />

      <DeleteConfirmDialog
        shipmentTitle={deletingShipment?.load_id || ''}
        isOpen={!!deletingShipment}
        onClose={() => setDeletingShipment(null)}
        onConfirm={confirmDelete}
        isLoading={deleteShipment.isPending}
      />
    </div>
  );
}

export default App;
