import { useState, useEffect } from 'react';
import { X, Phone, Clock, CheckCircle, XCircle, Filter, Loader2 } from 'lucide-react';
import { PhoneCall, CallType, SentimentType } from '../types';
import { api } from '../api';

interface AllPhoneCallsDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AllPhoneCallsDialog({ isOpen, onClose }: AllPhoneCallsDialogProps) {
  const [phoneCalls, setPhoneCalls] = useState<PhoneCall[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    call_type: '',
    agreed: '',
    sentiment: ''
  });

  const loadPhoneCalls = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const filterParams: any = {};
      if (filters.call_type) filterParams.call_type = filters.call_type;
      if (filters.agreed) filterParams.agreed = filters.agreed === 'true';
      if (filters.sentiment) filterParams.sentiment = filters.sentiment;

      const calls = await api.getAllPhoneCalls(filterParams);
      setPhoneCalls(calls);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load phone calls');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadPhoneCalls();
    }
  }, [isOpen, filters]);

  const getSentimentColor = (sentiment: SentimentType) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'neutral': return 'text-yellow-600 bg-yellow-100';
      case 'negative': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getCallTypeColor = (callType: CallType) => {
    switch (callType) {
      case 'agent': return 'text-blue-600 bg-blue-100';
      case 'manual': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <Phone className="h-6 w-6 text-primary-600" />
            <h2 className="text-2xl font-bold text-gray-900">All Phone Calls</h2>
            <span className="text-sm text-gray-500">({phoneCalls.length} calls)</span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Filters */}
        <div className="p-6 border-b bg-gray-50">
          <div className="flex items-center space-x-4">
            <Filter className="h-5 w-5 text-gray-500" />
            <div className="flex items-center space-x-4">
              <select
                value={filters.call_type}
                onChange={(e) => setFilters(prev => ({ ...prev, call_type: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Call Types</option>
                <option value="manual">Manual</option>
                <option value="agent">Agent</option>
              </select>

              <select
                value={filters.agreed}
                onChange={(e) => setFilters(prev => ({ ...prev, agreed: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Outcomes</option>
                <option value="true">Agreed</option>
                <option value="false">Not Agreed</option>
              </select>

              <select
                value={filters.sentiment}
                onChange={(e) => setFilters(prev => ({ ...prev, sentiment: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Sentiments</option>
                <option value="positive">Positive</option>
                <option value="neutral">Neutral</option>
                <option value="negative">Negative</option>
              </select>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
              <span className="ml-2 text-gray-600">Loading phone calls...</span>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <XCircle className="mx-auto h-12 w-12 text-red-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Error Loading Calls</h3>
              <p className="mt-1 text-sm text-gray-500">{error}</p>
              <button
                onClick={loadPhoneCalls}
                className="mt-4 btn btn-primary"
              >
                Retry
              </button>
            </div>
          ) : phoneCalls.length === 0 ? (
            <div className="text-center py-12">
              <Phone className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No phone calls found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {Object.values(filters).some(f => f) 
                  ? 'Try adjusting your filter criteria.'
                  : 'No phone calls have been recorded yet.'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {phoneCalls.map((call) => (
                <div key={call.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="font-medium text-gray-900">
                          {call.shipment_load_id || 'Unknown Load'}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCallTypeColor(call.call_type)}`}>
                          {call.call_type}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(call.sentiment)}`}>
                          {call.sentiment}
                        </span>
                        {call.agreed ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-500" />
                        )}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">Route:</span> {call.shipment_origin} → {call.shipment_destination}
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="h-4 w-4" />
                          <span>{Math.round(call.seconds / 60 * 10) / 10} minutes</span>
                        </div>
                        <div>
                          <span className="font-medium">Date:</span> {formatDate(call.created_at)}
                        </div>
                      </div>
                      
                      {call.notes && (
                        <div className="mt-2 text-sm text-gray-600">
                          <span className="font-medium">Notes:</span> {call.notes}
                        </div>
                      )}
                      
                      {call.call_id && (
                        <div className="mt-1 text-xs text-gray-500">
                          Call ID: {call.call_id}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <div className="text-sm text-gray-500">
            Showing {phoneCalls.length} phone calls
          </div>
          <button
            onClick={onClose}
            className="btn btn-secondary"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
