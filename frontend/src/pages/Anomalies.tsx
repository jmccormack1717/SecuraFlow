import { useEffect, useState } from 'react'
import { anomaliesApi } from '../services/api'
import { format } from 'date-fns'

export default function Anomalies() {
  const [anomalies, setAnomalies] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'resolved' | 'unresolved'>('unresolved')
  const [page, setPage] = useState(0)
  const limit = 50

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        setLoading(true)
        const resolved = filter === 'all' ? undefined : filter === 'resolved'
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
      server_error: 'bg-red-100 text-red-800',
      client_error: 'bg-orange-100 text-orange-800',
      response_time_spike: 'bg-yellow-100 text-yellow-800',
      large_request: 'bg-purple-100 text-purple-800',
      pattern_anomaly: 'bg-blue-100 text-blue-800',
    }
    return colors[type] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Anomalies</h2>
          <p className="text-gray-600 mt-1">Detected anomalies and alerts</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('unresolved')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'unresolved'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Unresolved
          </button>
          <button
            onClick={() => setFilter('resolved')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'resolved'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Resolved
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading anomalies...</div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Endpoint
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {anomalies.map((anomaly) => (
                  <tr key={anomaly.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {(anomaly.anomaly_score * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {anomaly.traffic_log?.endpoint || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {anomaly.is_resolved ? (
                        <span className="px-2 py-1 text-xs font-medium text-green-800 bg-green-100 rounded-full">
                          Resolved
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium text-red-800 bg-red-100 rounded-full">
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
            <div className="text-sm text-gray-700">
              Showing {page * limit + 1} to {Math.min((page + 1) * limit, total)} of {total}{' '}
              anomalies
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={(page + 1) * limit >= total}
                className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50"
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

