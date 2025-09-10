import { Shipment } from '../types';
import { format } from 'date-fns';
import { MapPin, Calendar, MoreVertical, Edit, Trash2 } from 'lucide-react';
import { useState } from 'react';

interface ShipmentItemProps {
  shipment: Shipment;
  onToggleStatus: (id: string, status: 'pending' | 'completed') => void;
  onEdit: (shipment: Shipment) => void;
  onDelete: (id: string) => void;
}

export function ShipmentItem({ shipment, onToggleStatus, onEdit, onDelete }: ShipmentItemProps) {
  const [showMenu, setShowMenu] = useState(false);

  const handleToggleStatus = () => {
    const newStatus = shipment.status === 'pending' ? 'completed' : 'pending';
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

  return (
    <div className="card p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          {/* Status Checkbox */}
          <input
            type="checkbox"
            checked={shipment.status === 'completed'}
            onChange={handleToggleStatus}
            className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            aria-label={`Mark ${shipment.title} as ${shipment.status === 'pending' ? 'completed' : 'pending'}`}
          />

          {/* Content */}
          <div className="flex-1 min-w-0">
            <h3 className={`text-lg font-medium ${
              shipment.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'
            }`}>
              {shipment.title}
            </h3>

            {shipment.destination && (
              <div className="flex items-center mt-1 text-sm text-gray-600">
                <MapPin className="h-4 w-4 mr-1" />
                <span>{shipment.destination}</span>
              </div>
            )}

            {shipment.eta && (
              <div className="flex items-center mt-1 text-sm text-gray-600">
                <Calendar className="h-4 w-4 mr-1" />
                <span>ETA: {format(new Date(shipment.eta), 'MMM dd, yyyy')}</span>
              </div>
            )}

            <div className="flex items-center mt-2 space-x-4 text-xs text-gray-500">
              <span>Created: {format(new Date(shipment.created_at), 'MMM dd, yyyy')}</span>
              {shipment.updated_at !== shipment.created_at && (
                <span>Updated: {format(new Date(shipment.updated_at), 'MMM dd, yyyy')}</span>
              )}
            </div>
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
