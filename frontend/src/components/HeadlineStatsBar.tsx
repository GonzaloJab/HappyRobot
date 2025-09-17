import { ShipmentStats } from '../types';
import { Package, TrendingUp, Clock } from 'lucide-react';

interface HeadlineStatsBarProps {
  stats: ShipmentStats;
  isLoading?: boolean;
}

export function HeadlineStatsBar({ stats, isLoading }: HeadlineStatsBarProps) {

  const formatMinutes = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes.toFixed(1)}m`;
    } else {
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      return `${hours}h ${remainingMinutes.toFixed(0)}m`;
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
      phoneStats: manualStats.phone_calls.manual, // Show manual call stats
      color: 'blue',
      icon: Package,
    },
    {
      title: 'URL/API (Agent)',
      subtitle: 'Assignments made via automated agents or integrations',
      stats: urlApiStats,
      phoneStats: urlApiStats.phone_calls.agent, // Show agent call stats
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

              {/* Total Minutes Spent - Prominent */}
              <div className="mb-4">
                <div className="flex items-baseline">
                  <Clock className={`h-5 w-5 ${colors.metric} mr-2`} />
                  <span className={`text-3xl font-bold ${colors.value}`}>
                    {formatMinutes(card.phoneStats.total_seconds / 60)}
                  </span>
                </div>
                <p className={`text-sm ${colors.metric} font-medium`}>
                  Total Minutes Spent
                </p>
              </div>

              {/* Phone Call metrics - Smaller */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className={`text-lg font-semibold ${colors.value}`}>
                    {card.phoneStats.total_calls}
                  </div>
                  <p className="text-xs text-gray-600">Total Calls</p>
                </div>
                <div>
                  <div className={`text-lg font-semibold ${colors.value}`}>
                    {card.phoneStats.agreed_calls}
                  </div>
                  <p className="text-xs text-gray-600">Successful Calls</p>
                </div>
                <div>
                  <div className={`text-lg font-semibold ${colors.value}`}>
                    {card.phoneStats.total_calls > 0 
                      ? `${((card.phoneStats.agreed_calls / card.phoneStats.total_calls) * 100).toFixed(1)}%`
                      : '0%'
                    }
                  </div>
                  <p className="text-xs text-gray-600">Success Rate</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
