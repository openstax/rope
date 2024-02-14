import { render, screen } from '@testing-library/react'
import { AuthContext, AuthStatus } from '../components/useAuthContext'
import { AuthGuard } from '../components/AuthGuard'
import { expect } from 'vitest'
import { PageContextProvider } from '../components/usePageContext'
import { type PageContext } from 'vike/types'

describe('AuthGuard', () => {
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

    const pageTitle = screen.queryByText('Protected content')
    expect(pageTitle).toBeNull()
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

    const pageTitle = screen.getByText('Protected content')
    expect(pageTitle).toBeInTheDocument()
  })
})
