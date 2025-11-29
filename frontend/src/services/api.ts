import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface TrafficData {
  endpoint: string
  method: string
  status_code: number
  response_time_ms: number
  request_size_bytes?: number
  response_size_bytes?: number
  ip_address?: string
  user_agent?: string
  timestamp?: string
}

export interface TrafficResponse {
  success: boolean
  anomaly_detected: boolean
  anomaly_score: number
  message?: string
}

export interface Metric {
  time_window: string
  endpoint?: string
  request_count: number
  avg_response_time_ms: number
  error_count: number
  p95_response_time_ms?: number
  p99_response_time_ms?: number
}

export interface Anomaly {
  id: number
  detected_at: string
  anomaly_score: number
  anomaly_type: string
  features?: Record<string, any>
  is_resolved: boolean
  traffic_log?: {
    id: number
    endpoint: string
    method: string
    status_code: number
    response_time_ms: number
    timestamp: string
  }
}

export interface HealthResponse {
  status: string
  database: string
  model_loaded: boolean
  uptime_seconds: number
}

// API functions
export const trafficApi = {
  ingest: async (data: TrafficData): Promise<TrafficResponse> => {
    const response = await api.post<TrafficResponse>('/api/traffic', data)
    return response.data
  },
}

export const metricsApi = {
  getMetrics: async (params?: {
    start_time?: string
    end_time?: string
    endpoint?: string
  }): Promise<{ metrics: Metric[]; total: number }> => {
    const response = await api.get<{ metrics: Metric[]; total: number }>(
      '/api/metrics',
      { params }
    )
    return response.data
  },
}

export const anomaliesApi = {
  getAnomalies: async (params?: {
    limit?: number
    offset?: number
    resolved?: boolean
  }): Promise<{
    anomalies: Anomaly[]
    total: number
    limit: number
    offset: number
  }> => {
    const response = await api.get<
      { anomalies: Anomaly[]; total: number; limit: number; offset: number }
    >('/api/anomalies', { params })
    return response.data
  },
}

export const healthApi = {
  check: async (): Promise<HealthResponse> => {
    const response = await api.get<HealthResponse>('/api/health')
    return response.data
  },
}

export default api

