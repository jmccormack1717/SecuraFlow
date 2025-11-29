import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout/Layout'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import Anomalies from './pages/Anomalies'
import Metrics from './pages/Metrics'
import ModelMetrics from './pages/ModelMetrics'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoading, token } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-gray-500 dark:text-gray-400">Loading...</div>
      </div>
    )
  }

  // Allow access if user has a token (either authenticated or demo)
  if (!token) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/anomalies"
        element={
          <ProtectedRoute>
            <Layout>
              <Anomalies />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/metrics"
        element={
          <ProtectedRoute>
            <Layout>
              <Metrics />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/model-metrics"
        element={
          <ProtectedRoute>
            <Layout>
              <ModelMetrics />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <AppRoutes />
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App

