import { Link, useLocation } from 'react-router-dom'

const navigation = [
  { name: 'Dashboard', href: '/', icon: '📊' },
  { name: 'Anomalies', href: '/anomalies', icon: '⚠️' },
  { name: 'Metrics', href: '/metrics', icon: '📈' },
  { name: 'Model Performance', href: '/model-metrics', icon: '🤖' },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 bg-white dark:bg-gray-800 shadow-sm min-h-screen border-r border-gray-200 dark:border-gray-700">
      <nav className="p-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <li key={item.name}>
                <Link
                  to={item.href}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  <span>{item.name}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </aside>
  )
}

