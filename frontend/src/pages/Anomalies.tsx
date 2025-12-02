import { useEffect, useState } from 'react'
import { anomaliesApi, Anomaly } from '../services/api'
import { format } from 'date-fns'

export default function Anomalies() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'unresolved'>('unresolved')
  const [page, setPage] = useState(0)
  const limit = 50

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        setLoading(true)
        const resolved = filter === 'all' ? undefined : false
        const data = await anomaliesApi.getAnomalies({
          limit,
          offset: page * limit,
          resolved,
        })
        setAnomalies(data.anomalies)
        setTotal(data.total)
      } catch (error) {
        console.error('Error fetching anomalies:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchAnomalies()
    const interval = setInterval(fetchAnomalies, 10000) // Refresh every 10 seconds

    return () => clearInterval(interval)
  }, [filter, page])

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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Anomalies</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Detected anomalies and alerts</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('unresolved')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'unresolved'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            Unresolved
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">Loading anomalies...</div>
      ) : anomalies.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400 text-lg">No anomalies found</p>
          <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">
            {filter === 'unresolved' 
              ? 'No unresolved anomalies detected. System is operating normally.'
              : 'No anomalies detected in the system.'}
          </p>
        </div>
      ) : (
        <>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Endpoint
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {anomalies.map((anomaly) => (
                  <tr key={anomaly.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {format(new Date(anomaly.detected_at), 'MMM dd, yyyy HH:mm:ss')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getAnomalyTypeColor(
                          anomaly.anomaly_type
                        )}`}
                      >
                        {anomaly.anomaly_type.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {(anomaly.anomaly_score * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {anomaly.traffic_log?.endpoint || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {anomaly.is_resolved ? (
                        <span className="px-2 py-1 text-xs font-medium text-green-800 dark:text-green-300 bg-green-100 dark:bg-green-900/30 rounded-full">
                          Resolved
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium text-red-800 dark:text-red-300 bg-red-100 dark:bg-red-900/30 rounded-full">
                          Active
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700 dark:text-gray-300">
              Showing {page * limit + 1} to {Math.min((page + 1) * limit, total)} of {total}{' '}
              anomalies
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={(page + 1) * limit >= total}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

