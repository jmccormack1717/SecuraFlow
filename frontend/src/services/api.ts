import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
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
  features?: Record<string, unknown>
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

export interface DemoDataResponse {
  success: boolean
  message: string
  traffic_logs_created: number
  anomalies_created: number
  time_range: {
    start: string
    end: string
  }
}

export const demoApi = {
  generate: async (params?: {
    count?: number
    anomaly_rate?: number
    hours_back?: number
  }): Promise<DemoDataResponse> => {
    const response = await api.post<DemoDataResponse>('/api/demo/generate', null, { params })
    return response.data
  },
}

export interface ModelPerformance {
  id: number
  model_version: string
  evaluation_date: string
  total_predictions: number
  true_positives: number
  false_positives: number
  true_negatives: number
  false_negatives: number
  precision: number
  recall: number
  f1_score: number
  accuracy: number
  auc_roc?: number
  avg_anomaly_score: number
  threshold_used: number
}

export const modelMetricsApi = {
  getMetrics: async (limit?: number): Promise<{ metrics: ModelPerformance[]; total: number }> => {
    const response = await api.get<{ metrics: ModelPerformance[]; total: number }>(
      '/api/model-metrics',
      { params: { limit } }
    )
    return response.data
  },
  evaluate: async (): Promise<ModelPerformance> => {
    const response = await api.post<ModelPerformance>('/api/model-metrics/evaluate')
    return response.data
  },
}

export interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export const authApi = {
  signup: async (email: string, username: string, password: string): Promise<User> => {
    const response = await api.post<User>('/api/auth/signup', {
      email,
      username,
      password,
    })
    return response.data
  },
  login: async (username: string, password: string): Promise<TokenResponse> => {
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    const response = await api.post<TokenResponse>('/api/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },
  demoLogin: async (): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/api/auth/demo')
    return response.data
  },
  getCurrentUser: async (token: string): Promise<User> => {
    const response = await api.get<User>('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    return response.data
  },
}

export default api

