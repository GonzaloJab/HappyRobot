import { FilterStatus, SortField, SortDirection } from '../types';
import { Search, Filter, Calendar, MapPin, Package } from 'lucide-react';

interface LoadFiltersBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: FilterStatus;
  onStatusFilterChange: (status: FilterStatus) => void;
  equipmentTypeFilter: string;
  onEquipmentTypeFilterChange: (type: string) => void;
  commodityTypeFilter: string;
  onCommodityTypeFilterChange: (type: string) => void;
  sortField: SortField;
  onSortFieldChange: (field: SortField) => void;
  sortDirection: SortDirection;
  onSortDirectionChange: (direction: SortDirection) => void;
}

export function LoadFiltersBar({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  equipmentTypeFilter,
  onEquipmentTypeFilterChange,
  commodityTypeFilter,
  onCommodityTypeFilterChange,
  sortField,
  onSortFieldChange,
  sortDirection,
  onSortDirectionChange,
}: LoadFiltersBarProps) {
  const statusOptions: { value: FilterStatus; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'pending', label: 'Pending' },
    { value: 'completed', label: 'Completed' },
  ];

  const equipmentTypeOptions = [
    { value: '', label: 'All Equipment' },
    { value: 'Dry Van', label: 'Dry Van' },
    { value: 'Reefer', label: 'Reefer' },
    { value: 'Flatbed', label: 'Flatbed' },
    { value: 'Container', label: 'Container' },
    { value: 'Tanker', label: 'Tanker' },
  ];

  const commodityTypeOptions = [
    { value: '', label: 'All Commodities' },
    { value: 'Electronics', label: 'Electronics' },
    { value: 'Produce', label: 'Produce' },
    { value: 'Machinery', label: 'Machinery' },
    { value: 'Textiles', label: 'Textiles' },
    { value: 'Food', label: 'Food' },
    { value: 'Industrial', label: 'Industrial' },
  ];

  const sortOptions: { value: SortField; label: string }[] = [
    { value: 'created_at', label: 'Created Date' },
    { value: 'pickup_datetime', label: 'Pickup Date' },
    { value: 'delivery_datetime', label: 'Delivery Date' },
    { value: 'loadboard_rate', label: 'Rate' },
    { value: 'miles', label: 'Miles' },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 space-y-6">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <input
          type="text"
          placeholder="Search by load ID, origin, destination, commodity, or notes..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="input pl-10"
        />
      </div>

      {/* Filters Row 1 */}
      <div className="flex flex-wrap gap-4 items-center">
        {/* Status Filter Pills */}
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Status:</span>
          <div className="flex gap-1">
            {statusOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => onStatusFilterChange(option.value)}
                className={`px-3 py-1 text-sm rounded-full transition-colors ${
                  statusFilter === option.value
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Equipment Type Filter */}
        <div className="flex items-center gap-2">
          <Package className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Equipment:</span>
          <select
            value={equipmentTypeFilter}
            onChange={(e) => onEquipmentTypeFilterChange(e.target.value)}
            className="input py-1 text-sm w-auto min-w-[120px]"
          >
            {equipmentTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Commodity Type Filter */}
        <div className="flex items-center gap-2">
          <Package className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Commodity:</span>
          <select
            value={commodityTypeFilter}
            onChange={(e) => onCommodityTypeFilterChange(e.target.value)}
            className="input py-1 text-sm w-auto min-w-[120px]"
          >
            {commodityTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Filters Row 2 - Sort Controls */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Sort by:</span>
          <select
            value={sortField}
            onChange={(e) => onSortFieldChange(e.target.value as SortField)}
            className="input py-1 text-sm w-auto min-w-[140px]"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <button
            onClick={() =>
              onSortDirectionChange(sortDirection === 'asc' ? 'desc' : 'asc')
            }
            className="btn btn-secondary py-1 px-2 text-sm"
            title={`Sort ${sortDirection === 'asc' ? 'descending' : 'ascending'}`}
          >
            {sortDirection === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>
    </div>
  );
}
