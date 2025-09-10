import { Shipment } from '../types';
import { Package, Clock, CheckCircle } from 'lucide-react';

interface StatsBarProps {
  shipments: Shipment[];
}

export function StatsBar({ shipments }: StatsBarProps) {
  const total = shipments.length;
  const pending = shipments.filter(s => s.status === 'pending').length;
  const completed = shipments.filter(s => s.status === 'completed').length;

  const stats = [
    {
      label: 'Total',
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
      label: 'Completed',
      value: completed,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <div key={stat.label} className={`${stat.bgColor} p-4 rounded-lg`}>
            <div className="flex items-center">
              <div className={`${stat.color} p-2 rounded-md`}>
                <Icon className="h-6 w-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
