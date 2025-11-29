import { useEffect, useState } from 'react'
import { metricsApi, anomaliesApi, healthApi } from '../services/api'
import TrafficChart from '../components/Dashboard/TrafficChart'
import MetricsCard from '../components/Dashboard/MetricsCard'
import AnomalyList from '../components/Dashboard/AnomalyList'
import SystemHealth from '../components/Dashboard/SystemHealth'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any[]>([])
  const [recentAnomalies, setRecentAnomalies] = useState<any[]>([])
  const [health, setHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsData, anomaliesData, healthData] = await Promise.all([
          metricsApi.getMetrics(),
          anomaliesApi.getAnomalies({ limit: 10, resolved: false }),
          healthApi.check(),
        ])

        setMetrics(metricsData.metrics)
        setRecentAnomalies(anomaliesData.anomalies)
        setHealth(healthData)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    )
  }

  // Calculate summary metrics
  const totalRequests = metrics.reduce((sum, m) => sum + m.request_count, 0)
  const avgResponseTime =
    metrics.length > 0
      ? metrics.reduce((sum, m) => sum + m.avg_response_time_ms, 0) / metrics.length
      : 0
  const totalErrors = metrics.reduce((sum, m) => sum + m.error_count, 0)
  const errorRate = totalRequests > 0 ? (totalErrors / totalRequests) * 100 : 0

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600 mt-1">Real-time API monitoring overview</p>
      </div>

      {/* System Health */}
      {health && <SystemHealth health={health} />}

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricsCard
          title="Total Requests"
          value={totalRequests.toLocaleString()}
          subtitle="Last hour"
        />
        <MetricsCard
          title="Avg Response Time"
          value={`${avgResponseTime.toFixed(0)}ms`}
          subtitle="Average"
        />
        <MetricsCard
          title="Error Rate"
          value={`${errorRate.toFixed(2)}%`}
          subtitle={`${totalErrors} errors`}
        />
        <MetricsCard
          title="Active Anomalies"
          value={recentAnomalies.length.toString()}
          subtitle="Unresolved"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TrafficChart metrics={metrics} />
        <AnomalyList anomalies={recentAnomalies} />
      </div>
    </div>
  )
}

