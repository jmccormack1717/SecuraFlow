import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { format } from 'date-fns'
import { Metric } from '../../services/api'

interface TrafficChartProps {
  metrics: Metric[]
}

export default function TrafficChart({ metrics }: TrafficChartProps) {
  const chartData = metrics
    .slice()
    .reverse()
    .map((metric) => ({
      time: format(new Date(metric.time_window), 'HH:mm'),
      requests: metric.request_count,
      avgResponseTime: metric.avg_response_time_ms,
      errors: metric.error_count,
    }))

  if (metrics.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Traffic Overview</h3>
        <div className="flex items-center justify-center h-64 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded">
          <p className="text-gray-400 dark:text-gray-500">No data available for the selected time range</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Traffic Overview</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="requests"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Requests"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="avgResponseTime"
            stroke="#ef4444"
            strokeWidth={2}
            name="Avg Response Time (ms)"
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="errors"
            stroke="#f59e0b"
            strokeWidth={2}
            name="Errors"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

