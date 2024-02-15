import { render, screen } from '@testing-library/react'
import { expect } from 'vitest'
import { Page } from '../pages/courses/+Page'

describe('Courses page', async () => {
  it('Renders Courses text', () => {
    render(<Page />)
    const pageTitle = screen.getByText('Courses')
    expect(pageTitle).toBeInTheDocument()
  })
})
