import { useEffect, useState } from 'react'
import { metricsApi } from '../services/api'
import TrafficChart from '../components/Dashboard/TrafficChart'

export default function Metrics() {
  const [metrics, setMetrics] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h'>('24h')

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
        console.log('Metrics data received:', data)
        setMetrics(data.metrics || [])
      } catch (error) {
        console.error('Error fetching metrics:', error)
        setMetrics([])
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
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Metrics</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Historical performance metrics</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setTimeRange('1h')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              timeRange === '1h'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            1 Hour
          </button>
          <button
            onClick={() => setTimeRange('6h')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              timeRange === '6h'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            6 Hours
          </button>
          <button
            onClick={() => setTimeRange('24h')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              timeRange === '24h'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            24 Hours
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">Loading metrics...</div>
      ) : metrics.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400 text-lg">No metrics found for the selected time range</p>
          <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">Try selecting a different time range or generate some traffic</p>
        </div>
      ) : (
        <div className="space-y-6">
          <TrafficChart metrics={metrics} />
          
          {/* Metrics Table */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Time Window
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Endpoint
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Requests
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Avg Response Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Errors
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    P95
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    P99
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {metrics.map((metric, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {new Date(metric.time_window).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {metric.endpoint || 'All'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {metric.request_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {metric.avg_response_time_ms.toFixed(0)}ms
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {metric.error_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {metric.p95_response_time_ms?.toFixed(0) || 'N/A'}ms
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
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

