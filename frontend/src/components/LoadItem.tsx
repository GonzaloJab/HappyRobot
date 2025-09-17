import { useState } from 'react';
import { Shipment, PhoneCallCreate } from '../types';
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
  Clock,
  Phone,
  X
} from 'lucide-react';

interface LoadItemProps {
  shipment: Shipment;
  onEdit: (shipment: Shipment) => void;
  onDelete: (id: string) => void;
  onAddPhoneCall?: (shipmentId: string, phoneCall: PhoneCallCreate) => void;
}

export function LoadItem({ shipment, onEdit, onDelete, onAddPhoneCall }: LoadItemProps) {
  const [showMenu, setShowMenu] = useState(false);
  const [showPhoneCallForm, setShowPhoneCallForm] = useState(false);
  const [phoneCallData, setPhoneCallData] = useState<PhoneCallCreate>({
    agreed: true,  // Always true for phone calls added to existing loads
    seconds: 0,
    call_type: 'manual',
    sentiment: 'neutral',
    notes: '',
    call_id: ''
  });

  const handleAssignManually = () => {
    onEdit(shipment);
    setShowMenu(false);
  };

  const handleDelete = () => {
    onDelete(shipment.id);
    setShowMenu(false);
  };

  const handleAddPhoneCall = () => {
    if (onAddPhoneCall) {
      // Automatically set agreed to true for phone calls added via LoadItem
      const phoneCallWithAgreed = {
        ...phoneCallData,
        agreed: true
      };
      onAddPhoneCall(shipment.id, phoneCallWithAgreed);
      setPhoneCallData({
        agreed: true,
        seconds: 0,
        call_type: 'manual',
        sentiment: 'neutral',
        notes: '',
        call_id: ''
      });
      setShowPhoneCallForm(false);
    }
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

            {/* Phone Call Stats */}
            {shipment.phone_calls && shipment.phone_calls.length > 0 && (
              <div className="mt-2">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-1 text-gray-600">
                    <Phone className="h-3 w-3" />
                    <span>Phone Calls:</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-gray-500">
                      {shipment.phone_calls.length} total
                    </span>
                    <span className="text-green-600">
                      {shipment.phone_calls.filter(call => call.agreed).length} agreed
                    </span>
                    <span className="text-blue-600">
                      {(shipment.phone_calls.reduce((total, call) => total + call.seconds, 0) / 60).toFixed(1)}m
                    </span>
                  </div>
                </div>
              </div>
            )}

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
                    onClick={handleAssignManually}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Assign Manually
                  </button>
                  {onAddPhoneCall && (
                    <button
                      onClick={() => {
                        setShowPhoneCallForm(true);
                        setShowMenu(false);
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-blue-600 hover:bg-blue-50"
                    >
                      <Phone className="h-4 w-4 mr-2" />
                      Add Phone Call
                    </button>
                  )}
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

      {/* Phone Call Form Modal */}
      {showPhoneCallForm && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-30"
            onClick={() => setShowPhoneCallForm(false)}
          />
          <div className="fixed inset-0 flex items-center justify-center z-40 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Phone className="h-5 w-5 mr-2" />
                    Add Phone Call
                  </h3>
                  <button
                    onClick={() => setShowPhoneCallForm(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Call Duration (seconds)
                      </label>
                      <input
                        type="number"
                        step="1"
                        min="0"
                        value={phoneCallData.seconds}
                        onChange={(e) => setPhoneCallData({...phoneCallData, seconds: parseFloat(e.target.value) || 0})}
                        className="input"
                        placeholder="0"
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

                  <div className="grid grid-cols-2 gap-3">
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

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Notes
                    </label>
                    <textarea
                      value={phoneCallData.notes}
                      onChange={(e) => setPhoneCallData({...phoneCallData, notes: e.target.value})}
                      className="input"
                      rows={3}
                      placeholder="Call notes..."
                    />
                  </div>

                </div>

                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    onClick={() => setShowPhoneCallForm(false)}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddPhoneCall}
                    className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Add Call
                  </button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
