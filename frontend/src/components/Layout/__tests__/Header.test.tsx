import { describe, it, expect } from 'vitest'
import { render, screen } from '../../../test/test-utils'
import Header from '../Header'

describe('Header', () => {
  it('renders SecuraFlow logo and title', () => {
    render(<Header />)
    expect(screen.getByText('SecuraFlow')).toBeInTheDocument()
    expect(screen.getByText('Real-time API Security & Monitoring')).toBeInTheDocument()
  })

  it('renders theme toggle button', () => {
    render(<Header />)
    const themeButton = screen.getByLabelText('Toggle theme')
    expect(themeButton).toBeInTheDocument()
  })

  it('has link to home page', () => {
    render(<Header />)
    const link = screen.getByRole('link', { name: /securaflow/i })
    expect(link).toHaveAttribute('href', '/')
  })
})

