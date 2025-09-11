import { Shipment } from '../types';
import { Package, Clock, CheckCircle, MapPin, DollarSign, Weight } from 'lucide-react';

interface LoadStatsBarProps {
  shipments: Shipment[];
}

export function LoadStatsBar({ shipments }: LoadStatsBarProps) {
  const total = shipments.length;
  const pending = shipments.filter(s => s.status === 'pending').length;
  const agreed = shipments.filter(s => s.status === 'agreed').length;
  
  // Calculate KPIs
  const totalMiles = shipments.reduce((sum, s) => sum + (s.miles || 0), 0);
  const totalPieces = shipments.reduce((sum, s) => sum + (s.num_of_pieces || 0), 0);
  const totalWeight = shipments.reduce((sum, s) => sum + (s.weight || 0), 0);
  const avgRate = shipments.length > 0 
    ? shipments.reduce((sum, s) => sum + (s.loadboard_rate || 0), 0) / shipments.length 
    : 0;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatWeight = (weight: number) => {
    if (weight >= 1000000) {
      return `${(weight / 1000000).toFixed(1)}M lbs`;
    } else if (weight >= 1000) {
      return `${(weight / 1000).toFixed(1)}K lbs`;
    }
    return `${weight.toLocaleString()} lbs`;
  };

  const stats = [
    {
      label: 'Total Loads',
      value: total,
      icon: Package,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      label: 'Pending',
      value: pending,
      icon: Clock,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      label: 'Assined',
      value: agreed,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      label: 'Total Miles',
      value: totalMiles.toLocaleString(),
      icon: MapPin,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      label: 'Total Pieces',
      value: totalPieces.toLocaleString(),
      icon: Package,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
    },
    {
      label: 'Total Weight',
      value: formatWeight(totalWeight),
      icon: Weight,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      label: 'Avg Rate',
      value: formatCurrency(avgRate),
      icon: DollarSign,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <div key={stat.label} className={`${stat.bgColor} p-4 rounded-lg`}>
            <div className="flex items-center">
              <div className={`${stat.color} p-2 rounded-md`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="ml-3">
                <p className="text-xs font-medium text-gray-600">{stat.label}</p>
                <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
