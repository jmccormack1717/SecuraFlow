import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { format } from 'date-fns'

interface TrafficChartProps {
  metrics: any[]
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

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Traffic Overview</h3>
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

