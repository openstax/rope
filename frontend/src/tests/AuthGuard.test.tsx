import { render, screen } from '@testing-library/react'
import { AuthContext, AuthStatus } from '../components/useAuthContext'
import { AuthGuard } from '../components/AuthGuard'
import { expect, vi } from 'vitest'
import { PageContextProvider } from '../components/usePageContext'
import { type PageContext } from 'vike/types'

describe('AuthGuard', () => {
  Object.defineProperty(window, 'location', {
    value: {
      href: './login'
    }
  })

  it('Authguard denies user protected content if user is not logged in', () => {
    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/about'
    } as PageContext

    render(
        <PageContextProvider pageContext={pageContext}>
      <AuthContext.Provider value={{ status: AuthStatus.NotSignedIn, isAdmin: false, isManager: false, email: 'rice@rice.edu' }}>
        <AuthGuard>
          <div>Protected content</div>
        </AuthGuard>
      </AuthContext.Provider>
      </PageContextProvider>
    )
    const protectedContent = screen.queryByText('Protected content')
    expect(protectedContent).toBeNull()
  })

  it('Authguard shows user protected content if user is logged in', () => {
    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/about'
    } as PageContext

    render(
        <PageContextProvider pageContext={pageContext}>
      <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: false, isManager: false, email: 'rice@rice.edu' }}>
        <AuthGuard>
          <div>Protected content</div>
        </AuthGuard>
      </AuthContext.Provider>
      </PageContextProvider>

    )

    const protectedContent = screen.getByText('Protected content')
    expect(protectedContent).toBeInTheDocument()
  })
})
