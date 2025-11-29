import { useEffect, useState } from 'react'
import { metricsApi, anomaliesApi, healthApi, demoApi } from '../services/api'
import TrafficChart from '../components/Dashboard/TrafficChart'
import MetricsCard from '../components/Dashboard/MetricsCard'
import AnomalyList from '../components/Dashboard/AnomalyList'
import SystemHealth from '../components/Dashboard/SystemHealth'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any[]>([])
  const [recentAnomalies, setRecentAnomalies] = useState<any[]>([])
  const [health, setHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

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

  const handleGenerateDemoData = async () => {
    try {
      setGenerating(true)
      const result = await demoApi.generate({
        count: 200,
        anomaly_rate: 0.15,
        hours_back: 24,
      })
      console.log('Demo data generated:', result)
      
      // Refresh data after generation
      const [metricsData, anomaliesData] = await Promise.all([
        metricsApi.getMetrics(),
        anomaliesApi.getAnomalies({ limit: 10, resolved: false }),
      ])
      setMetrics(metricsData.metrics)
      setRecentAnomalies(anomaliesData.anomalies)
      
      // Show success message
      alert(`Demo data generated successfully! Created ${result.traffic_logs_created} traffic logs with ${result.anomalies_created} anomalies.`)
    } catch (error) {
      console.error('Error generating demo data:', error)
      alert('Failed to generate demo data. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 dark:text-gray-400">Loading dashboard...</div>
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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Real-time API monitoring overview</p>
        </div>
        <button
          onClick={handleGenerateDemoData}
          disabled={generating}
          className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {generating ? (
            <>
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Generating...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Generate Demo Data</span>
            </>
          )}
        </button>
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

