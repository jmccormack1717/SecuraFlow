import { useEffect, useState } from 'react'
import { modelMetricsApi, ModelPerformance } from '../services/api'
import { format } from 'date-fns'

export default function ModelMetrics() {
  const [metrics, setMetrics] = useState<ModelPerformance[]>([])
  const [loading, setLoading] = useState(true)
  const [evaluating, setEvaluating] = useState(false)

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      setLoading(true)
      const data = await modelMetricsApi.getMetrics(10)
      setMetrics(data.metrics)
    } catch (error) {
      console.error('Error fetching model metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEvaluate = async () => {
    try {
      setEvaluating(true)
      await modelMetricsApi.evaluate()
      await fetchMetrics() // Refresh metrics
    } catch (error) {
      console.error('Error evaluating model:', error)
      alert('Failed to evaluate model. Please try again.')
    } finally {
      setEvaluating(false)
    }
  }

  const getMetricColor = (value: number, threshold: number = 0.7) => {
    if (value >= threshold) return 'text-green-600 dark:text-green-400'
    if (value >= threshold * 0.8) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  if (loading) {
    return (
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
        Loading model metrics...
      </div>
    )
  }

  const latestMetric = metrics[0]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Model Performance</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">ML model evaluation metrics and performance tracking</p>
        </div>
        <button
          onClick={handleEvaluate}
          disabled={evaluating}
          className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {evaluating ? (
            <>
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Evaluating...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span>Evaluate Model</span>
            </>
          )}
        </button>
      </div>

      {metrics.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400 text-lg">No model performance metrics available</p>
          <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">
            Click &quot;Evaluate Model&quot; to generate performance metrics based on recent predictions
          </p>
        </div>
      ) : (
        <>
          {/* Latest Metrics Summary */}
          {latestMetric && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Precision</h3>
                <p className={`text-3xl font-bold mt-2 ${getMetricColor(latestMetric.precision)}`}>
                  {(latestMetric.precision * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">True Positives / (TP + FP)</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Recall</h3>
                <p className={`text-3xl font-bold mt-2 ${getMetricColor(latestMetric.recall)}`}>
                  {(latestMetric.recall * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">True Positives / (TP + FN)</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">F1 Score</h3>
                <p className={`text-3xl font-bold mt-2 ${getMetricColor(latestMetric.f1_score)}`}>
                  {(latestMetric.f1_score * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Harmonic mean of P & R</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Accuracy</h3>
                <p className={`text-3xl font-bold mt-2 ${getMetricColor(latestMetric.accuracy)}`}>
                  {(latestMetric.accuracy * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">(TP + TN) / Total</p>
              </div>
            </div>
          )}

          {/* Confusion Matrix */}
          {latestMetric && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Confusion Matrix</h3>
              <div className="grid grid-cols-3 gap-4 max-w-md">
                <div></div>
                <div className="text-center font-medium text-gray-700 dark:text-gray-300">Predicted Normal</div>
                <div className="text-center font-medium text-gray-700 dark:text-gray-300">Predicted Anomaly</div>
                
                <div className="text-center font-medium text-gray-700 dark:text-gray-300 flex items-center">Actual Normal</div>
                <div className="bg-green-100 dark:bg-green-900/30 p-4 rounded text-center">
                  <div className="text-2xl font-bold text-green-800 dark:text-green-300">{latestMetric.true_negatives}</div>
                  <div className="text-xs text-green-600 dark:text-green-400 mt-1">True Negative</div>
                </div>
                <div className="bg-red-100 dark:bg-red-900/30 p-4 rounded text-center">
                  <div className="text-2xl font-bold text-red-800 dark:text-red-300">{latestMetric.false_positives}</div>
                  <div className="text-xs text-red-600 dark:text-red-400 mt-1">False Positive</div>
                </div>
                
                <div className="text-center font-medium text-gray-700 dark:text-gray-300 flex items-center">Actual Anomaly</div>
                <div className="bg-red-100 dark:bg-red-900/30 p-4 rounded text-center">
                  <div className="text-2xl font-bold text-red-800 dark:text-red-300">{latestMetric.false_negatives}</div>
                  <div className="text-xs text-red-600 dark:text-red-400 mt-1">False Negative</div>
                </div>
                <div className="bg-green-100 dark:bg-green-900/30 p-4 rounded text-center">
                  <div className="text-2xl font-bold text-green-800 dark:text-green-300">{latestMetric.true_positives}</div>
                  <div className="text-xs text-green-600 dark:text-green-400 mt-1">True Positive</div>
                </div>
              </div>
            </div>
          )}

          {/* Metrics History Table */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Evaluation Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Model Version
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Precision
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Recall
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    F1 Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Accuracy
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    Total Predictions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {metrics.map((metric) => (
                  <tr key={metric.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {format(new Date(metric.evaluation_date), 'MMM dd, yyyy HH:mm:ss')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {metric.model_version}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getMetricColor(metric.precision)}`}>
                      {(metric.precision * 100).toFixed(2)}%
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getMetricColor(metric.recall)}`}>
                      {(metric.recall * 100).toFixed(2)}%
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getMetricColor(metric.f1_score)}`}>
                      {(metric.f1_score * 100).toFixed(2)}%
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getMetricColor(metric.accuracy)}`}>
                      {(metric.accuracy * 100).toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {metric.total_predictions}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}



