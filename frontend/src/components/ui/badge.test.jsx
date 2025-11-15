import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Badge } from './badge'

describe('Badge Component', () => {
  it('renders badge with text', () => {
    render(<Badge>Test Badge</Badge>)
    expect(screen.getByText('Test Badge')).toBeInTheDocument()
  })

  it('applies default variant by default', () => {
    const { container } = render(<Badge>Default</Badge>)
    const badge = container.firstChild
    expect(badge).toHaveClass('bg-primary')
  })

  it('applies success variant when specified', () => {
    const { container } = render(<Badge variant="success">Success</Badge>)
    const badge = container.firstChild
    expect(badge).toHaveClass('bg-green-100')
  })

  it('applies warning variant when specified', () => {
    const { container } = render(<Badge variant="warning">Warning</Badge>)
    const badge = container.firstChild
    expect(badge).toHaveClass('bg-yellow-100')
  })

  it('applies error variant when specified', () => {
    const { container } = render(<Badge variant="error">Error</Badge>)
    const badge = container.firstChild
    expect(badge).toHaveClass('bg-red-100')
  })

  it('applies custom className', () => {
    const { container } = render(<Badge className="custom-class">Custom</Badge>)
    const badge = container.firstChild
    expect(badge).toHaveClass('custom-class')
  })

  it('renders as div element', () => {
    const { container } = render(<Badge>Div Badge</Badge>)
    expect(container.firstChild.tagName).toBe('DIV')
  })

  it('passes additional props to the element', () => {
    render(<Badge data-testid="test-badge">Props</Badge>)
    expect(screen.getByTestId('test-badge')).toBeInTheDocument()
  })
})
