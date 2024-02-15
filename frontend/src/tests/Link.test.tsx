import { render } from '@testing-library/react'
import { Link } from '../components/Link'
import { expect } from 'vitest'
import { PageContextProvider } from '../components/usePageContext'
import { type PageContext } from 'vike/types'

describe('Link component', () => {
  it('should render without is-active class', () => {
    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/other'
    } as PageContext

    const { container } = render(
      <PageContextProvider pageContext={pageContext}>
        <Link href="/about">Link Text</Link>
      </PageContextProvider>
    )

    expect(container.firstChild).not.toHaveClass('is-active')
  })
  it('should render is-active class', () => {
    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/about'
    } as PageContext

    const { container } = render(
      <PageContextProvider pageContext={pageContext}>
        <Link href="/about">Link Text</Link>
      </PageContextProvider>
    )

    expect(container.firstChild).toHaveClass('is-active')
  })
})
