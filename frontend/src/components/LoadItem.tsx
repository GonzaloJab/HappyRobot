import { useState } from 'react';
import { Shipment } from '../types';
import { format } from 'date-fns';
import { 
  MapPin, 
  Calendar, 
  MoreVertical, 
  Edit, 
  Trash2, 
  Package, 
  Weight, 
  Ruler,
  Truck,
  Clock
} from 'lucide-react';

interface LoadItemProps {
  shipment: Shipment;
  onToggleStatus: (id: string, status: 'pending' | 'agreed') => void;
  onEdit: (shipment: Shipment) => void;
  onDelete: (id: string) => void;
}

export function LoadItem({ shipment, onToggleStatus, onEdit, onDelete }: LoadItemProps) {
  const [showMenu, setShowMenu] = useState(false);

  const handleToggleStatus = () => {
    const newStatus = shipment.status === 'pending' ? 'agreed' : 'pending';
    onToggleStatus(shipment.id, newStatus);
  };

  const handleEdit = () => {
    onEdit(shipment);
    setShowMenu(false);
  };

  const handleDelete = () => {
    onDelete(shipment.id);
    setShowMenu(false);
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatWeight = (weight?: number) => {
    if (!weight) return 'N/A';
    return `${weight.toLocaleString()} lbs`;
  };

  return (
    <div className="card p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          {/* Status Checkbox */}
          <input
            type="checkbox"
            checked={shipment.status === 'agreed'}
            onChange={handleToggleStatus}
            className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            aria-label={`Mark ${shipment.load_id} as ${shipment.status === 'pending' ? 'agreed' : 'pending'}`}
          />

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Header with Load ID and Status */}
            <div className="flex items-center justify-between mb-2">
              <h3 className={`text-base font-semibold ${
                shipment.status === 'agreed' ? 'line-through text-gray-500' : 'text-gray-900'
              }`}>
                {shipment.load_id}
              </h3>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                shipment.status === 'agreed' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {shipment.status}
              </span>
            </div>

            {/* Route and Key Info Row */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <MapPin className="h-3 w-3 text-gray-400" />
                <span className="text-sm font-medium text-gray-900">
                  {shipment.origin} → {shipment.destination}
                </span>
              </div>
              <div className="flex items-center space-x-4 text-sm">
                {shipment.loadboard_rate && (
                  <span className="font-medium text-green-600">{formatCurrency(shipment.loadboard_rate)}</span>
                )}
                {shipment.agreed_price && (
                  <span className="font-medium text-blue-600">{formatCurrency(shipment.agreed_price)}</span>
                )}
                {shipment.miles && (
                  <span className="text-gray-600">{shipment.miles.toLocaleString()} mi</span>
                )}
              </div>
            </div>

            {/* Compact Details Row */}
            <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-1">
                  <Calendar className="h-3 w-3" />
                  <span>{format(new Date(shipment.pickup_datetime), 'MMM dd, HH:mm')}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>{format(new Date(shipment.delivery_datetime), 'MMM dd, HH:mm')}</span>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                {shipment.equipment_type && (
                  <span className="flex items-center space-x-1">
                    <Truck className="h-3 w-3" />
                    <span>{shipment.equipment_type}</span>
                  </span>
                )}
                {shipment.commodity_type && (
                  <span className="flex items-center space-x-1">
                    <Package className="h-3 w-3" />
                    <span>{shipment.commodity_type}</span>
                  </span>
                )}
                {shipment.carrier_description && (
                  <span className="flex items-center space-x-1">
                    <Truck className="h-3 w-3" />
                    <span>{shipment.carrier_description}</span>
                  </span>
                )}
              </div>
            </div>

            {/* Secondary Details Row */}
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center space-x-3">
                {shipment.weight && (
                  <span className="flex items-center space-x-1">
                    <Weight className="h-3 w-3" />
                    <span>{formatWeight(shipment.weight)}</span>
                  </span>
                )}
                {shipment.num_of_pieces && (
                  <span className="flex items-center space-x-1">
                    <Package className="h-3 w-3" />
                    <span>{shipment.num_of_pieces} pieces</span>
                  </span>
                )}
                {shipment.dimensions && (
                  <span className="flex items-center space-x-1">
                    <Ruler className="h-3 w-3" />
                    <span>{shipment.dimensions}</span>
                  </span>
                )}
              </div>
              <span>Created: {format(new Date(shipment.created_at), 'MMM dd')}</span>
            </div>

            {/* Notes (only if present) */}
            {shipment.notes && (
              <div className="mt-2">
                <p className="text-xs text-gray-600 bg-gray-50 p-2 rounded truncate" title={shipment.notes}>
                  {shipment.notes}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Actions Menu */}
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded"
            aria-label="More actions"
          >
            <MoreVertical className="h-5 w-5" />
          </button>

          {showMenu && (
            <>
              {/* Backdrop */}
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowMenu(false)}
              />
              
              {/* Menu */}
              <div className="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-20">
                <div className="py-1">
                  <button
                    onClick={handleEdit}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </button>
                  <button
                    onClick={handleDelete}
                    className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
