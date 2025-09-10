import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { ShipmentCreate, ShipmentUpdate } from '../types';
import { X, Calendar, MapPin, Package, DollarSign, Weight, Ruler } from 'lucide-react';

interface LoadFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ShipmentCreate | ShipmentUpdate) => void;
  isLoading?: boolean;
  initialData?: Partial<ShipmentCreate>;
  title?: string;
}

export function LoadForm({ 
  isOpen, 
  onClose, 
  onSubmit, 
  isLoading, 
  initialData,
  title = "Create New Load"
}: LoadFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<ShipmentCreate>({
    defaultValues: initialData
  });

  const pickupDatetime = watch('pickup_datetime');
  const deliveryDatetime = watch('delivery_datetime');

  const handleFormSubmit = (data: ShipmentCreate) => {
    onSubmit(data);
    reset();
    onClose();
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit(handleFormSubmit)} className="p-6 space-y-6">
            {/* Core Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Load ID */}
              <div>
                <label htmlFor="load_id" className="block text-sm font-medium text-gray-700 mb-1">
                  Load ID *
                </label>
                <input
                  {...register('load_id', { required: 'Load ID is required' })}
                  type="text"
                  id="load_id"
                  className="input"
                  placeholder="e.g., LD-2025-0001"
                />
                {errors.load_id && (
                  <p className="mt-1 text-sm text-red-600">{errors.load_id.message}</p>
                )}
              </div>

              {/* Equipment Type */}
              <div>
                <label htmlFor="equipment_type" className="block text-sm font-medium text-gray-700 mb-1">
                  Equipment Type
                </label>
                <select
                  {...register('equipment_type')}
                  id="equipment_type"
                  className="input"
                >
                  <option value="">Select equipment type</option>
                  <option value="Dry Van">Dry Van</option>
                  <option value="Reefer">Reefer</option>
                  <option value="Flatbed">Flatbed</option>
                  <option value="Container">Container</option>
                  <option value="Tanker">Tanker</option>
                </select>
              </div>
            </div>

            {/* Origin and Destination */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="origin" className="block text-sm font-medium text-gray-700 mb-1">
                  <MapPin className="inline h-4 w-4 mr-1" />
                  Origin *
                </label>
                <input
                  {...register('origin', { required: 'Origin is required' })}
                  type="text"
                  id="origin"
                  className="input"
                  placeholder="Origin location"
                />
                {errors.origin && (
                  <p className="mt-1 text-sm text-red-600">{errors.origin.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="destination" className="block text-sm font-medium text-gray-700 mb-1">
                  <MapPin className="inline h-4 w-4 mr-1" />
                  Destination *
                </label>
                <input
                  {...register('destination', { required: 'Destination is required' })}
                  type="text"
                  id="destination"
                  className="input"
                  placeholder="Destination location"
                />
                {errors.destination && (
                  <p className="mt-1 text-sm text-red-600">{errors.destination.message}</p>
                )}
              </div>
            </div>

            {/* Pickup and Delivery Times */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="pickup_datetime" className="block text-sm font-medium text-gray-700 mb-1">
                  <Calendar className="inline h-4 w-4 mr-1" />
                  Pickup Date & Time *
                </label>
                <input
                  {...register('pickup_datetime', { required: 'Pickup datetime is required' })}
                  type="datetime-local"
                  id="pickup_datetime"
                  className="input"
                />
                {errors.pickup_datetime && (
                  <p className="mt-1 text-sm text-red-600">{errors.pickup_datetime.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="delivery_datetime" className="block text-sm font-medium text-gray-700 mb-1">
                  <Calendar className="inline h-4 w-4 mr-1" />
                  Delivery Date & Time *
                </label>
                <input
                  {...register('delivery_datetime', { 
                    required: 'Delivery datetime is required',
                    validate: (value) => {
                      if (pickupDatetime && value <= pickupDatetime) {
                        return 'Delivery must be after pickup';
                      }
                      return true;
                    }
                  })}
                  type="datetime-local"
                  id="delivery_datetime"
                  className="input"
                />
                {errors.delivery_datetime && (
                  <p className="mt-1 text-sm text-red-600">{errors.delivery_datetime.message}</p>
                )}
              </div>
            </div>

            {/* Financial and Weight Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label htmlFor="loadboard_rate" className="block text-sm font-medium text-gray-700 mb-1">
                  <DollarSign className="inline h-4 w-4 mr-1" />
                  Loadboard Rate
                </label>
                <input
                  {...register('loadboard_rate', { min: 0 })}
                  type="number"
                  step="0.01"
                  id="loadboard_rate"
                  className="input"
                  placeholder="0.00"
                />
              </div>

              <div>
                <label htmlFor="weight" className="block text-sm font-medium text-gray-700 mb-1">
                  <Weight className="inline h-4 w-4 mr-1" />
                  Weight (lbs)
                </label>
                <input
                  {...register('weight', { min: 0 })}
                  type="number"
                  step="0.1"
                  id="weight"
                  className="input"
                  placeholder="0"
                />
              </div>

              <div>
                <label htmlFor="miles" className="block text-sm font-medium text-gray-700 mb-1">
                  Miles
                </label>
                <input
                  {...register('miles', { min: 0 })}
                  type="number"
                  step="0.1"
                  id="miles"
                  className="input"
                  placeholder="0"
                />
              </div>
            </div>

            {/* Commodity and Pieces */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="commodity_type" className="block text-sm font-medium text-gray-700 mb-1">
                  <Package className="inline h-4 w-4 mr-1" />
                  Commodity Type
                </label>
                <input
                  {...register('commodity_type')}
                  type="text"
                  id="commodity_type"
                  className="input"
                  placeholder="e.g., Electronics, Produce, Machinery"
                />
              </div>

              <div>
                <label htmlFor="num_of_pieces" className="block text-sm font-medium text-gray-700 mb-1">
                  Number of Pieces
                </label>
                <input
                  {...register('num_of_pieces', { min: 0 })}
                  type="number"
                  id="num_of_pieces"
                  className="input"
                  placeholder="0"
                />
              </div>
            </div>

            {/* Dimensions */}
            <div>
              <label htmlFor="dimensions" className="block text-sm font-medium text-gray-700 mb-1">
                <Ruler className="inline h-4 w-4 mr-1" />
                Dimensions
              </label>
              <input
                {...register('dimensions')}
                type="text"
                id="dimensions"
                className="input"
                placeholder="e.g., 48x40x60 in, 6m x 2m x 2m"
              />
            </div>

            {/* Notes */}
            <div>
              <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                {...register('notes')}
                id="notes"
                rows={3}
                className="input"
                placeholder="Additional notes or special instructions..."
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
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
                {isLoading ? 'Saving...' : 'Save Load'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
