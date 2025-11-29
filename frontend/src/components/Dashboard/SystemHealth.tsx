interface SystemHealthProps {
  health: {
    status: string
    database: string
    model_loaded: boolean
    uptime_seconds: number
  }
}

export default function SystemHealth({ health }: SystemHealthProps) {
  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    return `${hours}h ${minutes}m ${secs}s`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800'
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-red-100 text-red-800'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p className="text-sm text-gray-500">Status</p>
          <span
            className={`inline-block mt-1 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
              health.status
            )}`}
          >
            {health.status.toUpperCase()}
          </span>
        </div>
        <div>
          <p className="text-sm text-gray-500">Database</p>
          <p className="text-sm font-medium text-gray-900 mt-1">
            {health.database === 'connected' ? '✓ Connected' : '✗ Disconnected'}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">ML Model</p>
          <p className="text-sm font-medium text-gray-900 mt-1">
            {health.model_loaded ? '✓ Loaded' : '✗ Not Loaded'}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Uptime</p>
          <p className="text-sm font-medium text-gray-900 mt-1">
            {formatUptime(health.uptime_seconds)}
          </p>
        </div>
      </div>
    </div>
  )
}

