import { useForm } from 'react-hook-form';
import { ShipmentCreate, ShipmentUpdate, PhoneCallCreate } from '../types';
import { X, Calendar, MapPin, Package, DollarSign, Weight, Ruler, Phone } from 'lucide-react';
import { useEffect, useState } from 'react';

interface LoadFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ShipmentCreate | ShipmentUpdate, phoneCall?: PhoneCallCreate) => void;
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
    setValue,
  } = useForm<ShipmentCreate | ShipmentUpdate>({
    defaultValues: initialData
  });

  const [phoneCallData, setPhoneCallData] = useState<PhoneCallCreate>({
    agreed: true,  // Always true when phone call fields are shown (status = 'agreed')
    seconds: 0,
    call_type: 'manual',
    sentiment: 'neutral',
    notes: '',
    call_id: ''
  });

  const pickupDatetime = watch('pickup_datetime');
  const status = watch('status' as any);

  // Reset form when initialData changes
  useEffect(() => {
    if (initialData) {
      // Format dates for datetime-local input (YYYY-MM-DDTHH:MM)
      const formattedData = {
        ...initialData,
        pickup_datetime: initialData.pickup_datetime 
          ? new Date(initialData.pickup_datetime).toISOString().slice(0, 16)
          : initialData.pickup_datetime,
        delivery_datetime: initialData.delivery_datetime 
          ? new Date(initialData.delivery_datetime).toISOString().slice(0, 16)
          : initialData.delivery_datetime,
      };
      reset(formattedData);
    }
  }, [initialData, reset]);

  const handleFormSubmit = (data: ShipmentCreate | ShipmentUpdate) => {
    // Convert datetime-local format back to ISO format for API
    const formattedData = {
      ...data,
      pickup_datetime: data.pickup_datetime 
        ? new Date(data.pickup_datetime).toISOString()
        : data.pickup_datetime,
      delivery_datetime: data.delivery_datetime 
        ? new Date(data.delivery_datetime).toISOString()
        : data.delivery_datetime,
    };
    
    // If status is 'agreed' and phone call data is provided, include it in submission
    const status = 'status' in data ? data.status : undefined;
    const phoneCall = (status === 'agreed' && phoneCallData.seconds > 0) ? {
      ...phoneCallData,
      agreed: true  // Automatically set to true when status is 'agreed'
    } : undefined;
    onSubmit(formattedData, phoneCall);
    reset();
    setPhoneCallData({
      agreed: true,
      seconds: 0,
      call_type: 'manual',
      sentiment: 'neutral',
      notes: '',
      call_id: ''
    });
    onClose();
  };


  const handleClose = () => {
    reset();
    setPhoneCallData({
      agreed: true,
      seconds: 0,
      call_type: 'manual',
      sentiment: 'neutral',
      notes: '',
      call_id: ''
    });
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
                  <option value="agreed">Agreed</option>
                </select>
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
                      if (!value) return true; // Let required validation handle empty values
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

            {/* Status Indicator */}
            {status === 'agreed' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-blue-800">
                      <strong>Load Status: Agreed</strong> - Agreed Price and Carrier Description are required.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Financial and Weight Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
                <label htmlFor="agreed_price" className="block text-sm font-medium text-gray-700 mb-1">
                  <DollarSign className="inline h-4 w-4 mr-1" />
                  Agreed Price {status === 'agreed' && <span className="text-red-500">*</span>}
                </label>
                <input
                  {...register('agreed_price', { 
                    min: 0,
                    required: status === 'agreed' ? 'Agreed price is required when status is agreed' : false
                  })}
                  type="number"
                  step="0.01"
                  id="agreed_price"
                  className="input"
                  placeholder="0.00"
                />
                {errors.agreed_price && (
                  <p className="mt-1 text-sm text-red-600">{errors.agreed_price.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="carrier_description" className="block text-sm font-medium text-gray-700 mb-1">
                  Carrier Description {status === 'agreed' && <span className="text-red-500">*</span>}
                </label>
                <input
                  {...register('carrier_description', {
                    required: status === 'agreed' ? 'Carrier description is required when status is agreed' : false
                  })}
                  type="text"
                  id="carrier_description"
                  className="input"
                  placeholder="Carrier name or description"
                />
                {errors.carrier_description && (
                  <p className="mt-1 text-sm text-red-600">{errors.carrier_description.message}</p>
                )}
              </div>


              {/* Phone Call Fields - Show when status is 'agreed' */}
              {status === 'agreed' && (
                <div className="md:col-span-2">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-blue-800 flex items-center mb-4">
                      <Phone className="h-4 w-4 mr-1" />
                      Phone Call Details (Required for Agreed Status)
                    </h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Call Duration (seconds) *
                        </label>
                        <input
                          type="number"
                          step="1"
                          min="0"
                          value={phoneCallData.seconds}
                          onChange={(e) => setPhoneCallData({...phoneCallData, seconds: parseFloat(e.target.value) || 0})}
                          className="input"
                          placeholder="0"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Call ID
                        </label>
                        <input
                          type="text"
                          value={phoneCallData.call_id}
                          onChange={(e) => setPhoneCallData({...phoneCallData, call_id: e.target.value})}
                          className="input"
                          placeholder="Optional"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Call Type
                        </label>
                        <select
                          value={phoneCallData.call_type}
                          onChange={(e) => setPhoneCallData({...phoneCallData, call_type: e.target.value as 'manual' | 'agent'})}
                          className="input"
                        >
                          <option value="manual">Manual</option>
                          <option value="agent">Agent</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Sentiment
                        </label>
                        <select
                          value={phoneCallData.sentiment}
                          onChange={(e) => setPhoneCallData({...phoneCallData, sentiment: e.target.value as 'positive' | 'neutral' | 'negative'})}
                          className="input"
                        >
                          <option value="positive">Positive</option>
                          <option value="neutral">Neutral</option>
                          <option value="negative">Negative</option>
                        </select>
                      </div>
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Call Notes
                      </label>
                      <textarea
                        value={phoneCallData.notes}
                        onChange={(e) => setPhoneCallData({...phoneCallData, notes: e.target.value})}
                        className="input"
                        rows={3}
                        placeholder="Describe the call outcome, carrier response, etc..."
                      />
                    </div>

                  </div>
                </div>
              )}

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
            <div className="flex justify-between items-center pt-4 border-t border-gray-200">
              {/* Quick Assign Button */}
              {status !== 'agreed' && (
                <button
                  type="button"
                  onClick={() => {
                    // Set status to agreed and focus on agreed price field
                    setValue('status', 'agreed');
                    setTimeout(() => {
                      const form = document.getElementById('agreed_price') as HTMLInputElement;
                      if (form) {
                        form.focus();
                      }
                    }, 100);
                  }}
                  className="btn btn-outline-primary"
                  disabled={isLoading}
                >
                  Quick Assign Load
                </button>
              )}
              
              {/* Right side buttons */}
              <div className="flex space-x-3">
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
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
