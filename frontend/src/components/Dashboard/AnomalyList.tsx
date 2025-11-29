import { Link } from 'react-router-dom'
import { format } from 'date-fns'

interface AnomalyListProps {
  anomalies: any[]
}

export default function AnomalyList({ anomalies }: AnomalyListProps) {
  const getAnomalyTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      server_error: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300',
      client_error: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300',
      response_time_spike: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
      large_request: 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300',
      pattern_anomaly: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
    }
    return colors[type] || 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Anomalies</h3>
        <Link
          to="/anomalies"
          className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
        >
          View all →
        </Link>
      </div>
      {anomalies.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <p>No anomalies detected</p>
          <p className="text-sm mt-1">System is operating normally</p>
        </div>
      ) : (
        <div className="space-y-3">
          {anomalies.slice(0, 5).map((anomaly) => (
            <div
              key={anomaly.id}
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${getAnomalyTypeColor(
                        anomaly.anomaly_type
                      )}`}
                    >
                      {anomaly.anomaly_type.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {(anomaly.anomaly_score * 100).toFixed(1)}% confidence
                    </span>
                  </div>
                  <p className="text-sm text-gray-900 dark:text-white font-medium">
                    {anomaly.traffic_log?.endpoint || 'Unknown endpoint'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {format(new Date(anomaly.detected_at), 'MMM dd, yyyy HH:mm:ss')}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

