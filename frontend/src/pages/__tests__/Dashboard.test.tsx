import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '../../test/test-utils'
import Dashboard from '../Dashboard'
import * as api from '../../services/api'

// Mock the API
vi.mock('../../services/api', () => ({
  metricsApi: {
    getMetrics: vi.fn(),
  },
  anomaliesApi: {
    getAnomalies: vi.fn(),
  },
  healthApi: {
    check: vi.fn(),
  },
}))

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Default mock responses
    vi.mocked(api.metricsApi.getMetrics).mockResolvedValue({
      metrics: [],
      total: 0,
    })
    vi.mocked(api.anomaliesApi.getAnomalies).mockResolvedValue({
      anomalies: [],
      total: 0,
      limit: 10,
      offset: 0,
    })
    vi.mocked(api.healthApi.check).mockResolvedValue({
      status: 'healthy',
      database: 'connected',
      model_loaded: true,
      uptime_seconds: 100,
    })
  })

  it('renders dashboard title', () => {
    render(<Dashboard />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('displays loading state initially', () => {
    render(<Dashboard />)
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument()
  })

  it('fetches and displays metrics', async () => {
    vi.mocked(api.metricsApi.getMetrics).mockResolvedValue({
      metrics: [
        {
          time_window: new Date().toISOString(),
          request_count: 100,
          avg_response_time_ms: 50,
          error_count: 5,
        },
      ],
      total: 1,
    })

    render(<Dashboard />)

    await waitFor(() => {
      expect(api.metricsApi.getMetrics).toHaveBeenCalled()
    })
  })
})

