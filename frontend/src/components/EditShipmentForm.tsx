import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Shipment, ShipmentUpdate } from '../types';
import { X, Calendar } from 'lucide-react';

interface EditShipmentFormProps {
  shipment: Shipment | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (id: string, data: ShipmentUpdate) => void;
  isLoading?: boolean;
}

export function EditShipmentForm({ shipment, isOpen, onClose, onSubmit, isLoading }: EditShipmentFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<ShipmentUpdate>();

  const etaValue = watch('eta');

  // Reset form when shipment changes
  useEffect(() => {
    if (shipment) {
      reset({
        title: shipment.title,
        destination: shipment.destination || '',
        eta: shipment.eta ? shipment.eta.split('T')[0] : '',
        status: shipment.status,
      });
    }
  }, [shipment, reset]);

  const handleFormSubmit = (data: ShipmentUpdate) => {
    if (shipment) {
      onSubmit(shipment.id, data);
      onClose();
    }
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  if (!isOpen || !shipment) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Edit Shipment</h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit(handleFormSubmit)} className="p-6 space-y-4">
            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                Title *
              </label>
              <input
                {...register('title', { required: 'Title is required' })}
                type="text"
                id="title"
                className="input"
                placeholder="Enter shipment title"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            {/* Destination */}
            <div>
              <label htmlFor="destination" className="block text-sm font-medium text-gray-700 mb-1">
                Destination
              </label>
              <input
                {...register('destination')}
                type="text"
                id="destination"
                className="input"
                placeholder="Enter destination address"
              />
            </div>

            {/* ETA */}
            <div>
              <label htmlFor="eta" className="block text-sm font-medium text-gray-700 mb-1">
                Estimated Time of Arrival
              </label>
              <div className="relative">
                <input
                  {...register('eta')}
                  type="date"
                  id="eta"
                  className="input pr-10"
                />
                <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
              </div>
            </div>

            {/* Status */}
            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                {...register('status')}
                id="status"
                className="input"
              >
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                className="btn btn-secondary"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isLoading}
              >
                {isLoading ? 'Updating...' : 'Update Shipment'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
