import { Link } from 'react-router-dom'
import { format } from 'date-fns'

interface AnomalyListProps {
  anomalies: any[]
}

export default function AnomalyList({ anomalies }: AnomalyListProps) {
  const getAnomalyTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      server_error: 'bg-red-100 text-red-800',
      client_error: 'bg-orange-100 text-orange-800',
      response_time_spike: 'bg-yellow-100 text-yellow-800',
      large_request: 'bg-purple-100 text-purple-800',
      pattern_anomaly: 'bg-blue-100 text-blue-800',
    }
    return colors[type] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Recent Anomalies</h3>
        <Link
          to="/anomalies"
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          View all →
        </Link>
      </div>
      {anomalies.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No anomalies detected</p>
          <p className="text-sm mt-1">System is operating normally</p>
        </div>
      ) : (
        <div className="space-y-3">
          {anomalies.slice(0, 5).map((anomaly) => (
            <div
              key={anomaly.id}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
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
                    <span className="text-xs text-gray-500">
                      {(anomaly.anomaly_score * 100).toFixed(1)}% confidence
                    </span>
                  </div>
                  <p className="text-sm text-gray-900 font-medium">
                    {anomaly.traffic_log?.endpoint || 'Unknown endpoint'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
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

