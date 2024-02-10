import { render, screen } from '@testing-library/react'
import { expect } from 'vitest'
import { Page } from '../pages/about/+Page'

test('renders page title', async () => {
  render(<Page />)
  const pageTitle = screen.getByText('About')
  expect(pageTitle).toBeInTheDocument()
})
