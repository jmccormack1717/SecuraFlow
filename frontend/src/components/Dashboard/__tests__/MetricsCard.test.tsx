import { describe, it, expect } from 'vitest'
import { render, screen } from '../../../test/test-utils'
import MetricsCard from '../MetricsCard'

describe('MetricsCard', () => {
  it('renders title and value', () => {
    render(<MetricsCard title="Test Metric" value="100" />)
    expect(screen.getByText('Test Metric')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
  })

  it('renders subtitle when provided', () => {
    render(<MetricsCard title="Test" value="100" subtitle="Last hour" />)
    expect(screen.getByText('Last hour')).toBeInTheDocument()
  })

  it('does not render subtitle when not provided', () => {
    render(<MetricsCard title="Test" value="100" />)
    expect(screen.queryByText('Last hour')).not.toBeInTheDocument()
  })
})

