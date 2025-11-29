import { useEffect, useState } from 'react'
import { metricsApi } from '../services/api'
import TrafficChart from '../components/Dashboard/TrafficChart'

export default function Metrics() {
  const [metrics, setMetrics] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h'>('1h')

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true)
        const endTime = new Date()
        const startTime = new Date()
        
        switch (timeRange) {
          case '1h':
            startTime.setHours(startTime.getHours() - 1)
            break
          case '6h':
            startTime.setHours(startTime.getHours() - 6)
            break
          case '24h':
            startTime.setHours(startTime.getHours() - 24)
            break
        }

        const data = await metricsApi.getMetrics({
          start_time: startTime.toISOString(),
          end_time: endTime.toISOString(),
        })
        setMetrics(data.metrics)
      } catch (error) {
        console.error('Error fetching metrics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
    const interval = setInterval(fetchMetrics, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [timeRange])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Metrics</h2>
          <p className="text-gray-600 mt-1">Historical performance metrics</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setTimeRange('1h')}
            className={`px-4 py-2 rounded-lg ${
              timeRange === '1h'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            1 Hour
          </button>
          <button
            onClick={() => setTimeRange('6h')}
            className={`px-4 py-2 rounded-lg ${
              timeRange === '6h'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            6 Hours
          </button>
          <button
            onClick={() => setTimeRange('24h')}
            className={`px-4 py-2 rounded-lg ${
              timeRange === '24h'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            24 Hours
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading metrics...</div>
      ) : (
        <div className="space-y-6">
          <TrafficChart metrics={metrics} />
          
          {/* Metrics Table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Time Window
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Endpoint
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Requests
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Avg Response Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Errors
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    P95
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    P99
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {metrics.map((metric, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(metric.time_window).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {metric.endpoint || 'All'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {metric.request_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {metric.avg_response_time_ms.toFixed(0)}ms
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {metric.error_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {metric.p95_response_time_ms?.toFixed(0) || 'N/A'}ms
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {metric.p99_response_time_ms?.toFixed(0) || 'N/A'}ms
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

