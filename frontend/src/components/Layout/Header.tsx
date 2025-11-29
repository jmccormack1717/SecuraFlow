import { Link } from 'react-router-dom'

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">SF</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">SecuraFlow</h1>
          </Link>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">API Monitoring Dashboard</span>
          </div>
        </div>
      </div>
    </header>
  )
}

