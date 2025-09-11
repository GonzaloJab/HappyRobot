import { ShipmentStats } from '../types';
import { Clock, Package, TrendingUp } from 'lucide-react';

interface HeadlineStatsBarProps {
  stats: ShipmentStats;
  isLoading?: boolean;
}

export function HeadlineStatsBar({ stats, isLoading }: HeadlineStatsBarProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}s`;
    } else if (seconds < 3600) {
      return `${(seconds / 60).toFixed(1)}m`;
    } else {
      return `${(seconds / 3600).toFixed(1)}h`;
    }
  };

  if (isLoading) {
    return (
      <div className="mb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow-sm border p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="space-y-3">
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="h-6 bg-gray-200 rounded"></div>
                  <div className="h-6 bg-gray-200 rounded"></div>
                  <div className="h-6 bg-gray-200 rounded"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const manualStats = stats.manual;
  const urlApiStats = stats.url_api;

  const statCards = [
    {
      title: 'Manual (Frontend)',
      subtitle: 'Assignments made through the web UI',
      stats: manualStats,
      color: 'blue',
      icon: Package,
    },
    {
      title: 'URL/API (Agent)',
      subtitle: 'Assignments made via automated agents or integrations',
      stats: urlApiStats,
      color: 'green',
      icon: TrendingUp,
    },
  ];

  return (
    <div className="mb-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {statCards.map((card) => {
          const Icon = card.icon;
          const colorClasses = {
            blue: {
              bg: 'bg-blue-50',
              border: 'border-blue-200',
              icon: 'text-blue-600',
              title: 'text-blue-900',
              value: 'text-blue-700',
              metric: 'text-blue-600',
            },
            green: {
              bg: 'bg-green-50',
              border: 'border-green-200',
              icon: 'text-green-600',
              title: 'text-green-900',
              value: 'text-green-700',
              metric: 'text-green-600',
            },
          };

          const colors = colorClasses[card.color as keyof typeof colorClasses];

          return (
            <div
              key={card.title}
              className={`${colors.bg} ${colors.border} border rounded-lg p-6 shadow-sm`}
            >
              <div className="flex items-center mb-4">
                <div className={`${colors.icon} p-2 rounded-md bg-white`}>
                  <Icon className="h-6 w-6" />
                </div>
                <div className="ml-3">
                  <h3 className={`text-lg font-semibold ${colors.title}`}>
                    {card.title}
                  </h3>
                  <p className="text-sm text-gray-600">{card.subtitle}</p>
                </div>
              </div>

              {/* Average Time per Call - Prominent */}
              <div className="mb-4">
                <div className="flex items-baseline">
                  <Clock className={`h-5 w-5 ${colors.metric} mr-2`} />
                  <span className={`text-3xl font-bold ${colors.value}`}>
                    {formatTime(card.stats.avg_time_per_call_seconds)}
                  </span>
                </div>
                <p className={`text-sm ${colors.metric} font-medium`}>
                  Average Time per Call
                </p>
              </div>

              {/* Other metrics - Smaller */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className={`text-lg font-semibold ${colors.value}`}>
                    {card.stats.count}
                  </div>
                  <p className="text-xs text-gray-600">Assigned Loads</p>
                </div>
                <div>
                  <div className={`text-lg font-semibold ${colors.value}`}>
                    {formatCurrency(card.stats.total_agreed_price)}
                  </div>
                  <p className="text-xs text-gray-600">Total Agreed Price</p>
                </div>
                <div>
                  <div className={`text-lg font-semibold ${colors.value}`}>
                    {formatCurrency(card.stats.total_agreed_minus_loadboard)}
                  </div>
                  <p className="text-xs text-gray-600">Price Difference</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
