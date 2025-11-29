import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import Layout from './components/Layout/Layout'
import Dashboard from './pages/Dashboard'
import Anomalies from './pages/Anomalies'
import Metrics from './pages/Metrics'

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/anomalies" element={<Anomalies />} />
            <Route path="/metrics" element={<Metrics />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  )
}

export default App

