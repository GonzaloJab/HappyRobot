import { FilterStatus, SortField, SortDirection } from '../types';
import { Search, Filter } from 'lucide-react';

interface FiltersBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: FilterStatus;
  onStatusFilterChange: (status: FilterStatus) => void;
  sortField: SortField;
  onSortFieldChange: (field: SortField) => void;
  sortDirection: SortDirection;
  onSortDirectionChange: (direction: SortDirection) => void;
}

export function FiltersBar({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  sortField,
  onSortFieldChange,
  sortDirection,
  onSortDirectionChange,
}: FiltersBarProps) {
  const statusOptions: { value: FilterStatus; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'pending', label: 'Pending' },
    { value: 'completed', label: 'Completed' },
  ];

  const sortOptions: { value: SortField; label: string }[] = [
    { value: 'created_at', label: 'Created Date' },
    { value: 'eta', label: 'ETA' },
    { value: 'title', label: 'Title' },
  ];

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <input
          type="text"
          placeholder="Search by title or destination..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="input pl-10"
        />
      </div>

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

        {/* Sort Controls */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Sort by:</span>
          <select
            value={sortField}
            onChange={(e) => onSortFieldChange(e.target.value as SortField)}
            className="input py-1 text-sm w-auto"
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
