import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout/Layout'
import Dashboard from './pages/Dashboard'
import Anomalies from './pages/Anomalies'
import Metrics from './pages/Metrics'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/anomalies" element={<Anomalies />} />
          <Route path="/metrics" element={<Metrics />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App

