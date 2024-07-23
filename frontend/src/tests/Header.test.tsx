import { fireEvent, render, screen } from '@testing-library/react'
import { Header } from '../components/Header'
import { expect, vi } from 'vitest'
import { PageContextProvider } from '../components/usePageContext'
import type { PageContext } from 'vike/types'
import { AuthContext, AuthStatus } from '../components/useAuthContext'

describe('Header component', () => {
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
  const pageContext = {
    urlPathname: '/login'
  } as PageContext

  it('Header with logout button and authenticated user', () => {
    const logoutMock = vi.fn()

    render(
      <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: true, email: 'rice@rice.edu' }}>
      <PageContextProvider pageContext={pageContext}>
        <Header logout={logoutMock} >Link Text</Header>
      </PageContextProvider>
      </AuthContext.Provider>
    )
    const courses = screen.getByText('Courses')
    expect(courses).toBeInTheDocument()
    const logout = screen.getByText('Logout')
    expect(logout).toBeInTheDocument()
    const home = screen.getByText('Home')
    expect(home).toBeInTheDocument()

    fireEvent.click(logout)
    expect(logoutMock).toHaveBeenCalledTimes(1)
  })
  it('Header without logout button when user is not logged in', () => {
    render(
      <AuthContext.Provider value={{ status: AuthStatus.NotSignedIn, isAdmin: false, isManager: false, email: 'rice@rice.edu' }}>
      <PageContextProvider pageContext={pageContext}>
        <Header logout={vi.fn()} >Link Text</Header>
      </PageContextProvider>
      </AuthContext.Provider>
    )
    const courses = screen.getByText('Courses')
    expect(courses).toBeInTheDocument()
    const home = screen.getByText('Home')
    expect(home).toBeInTheDocument()
    const logout = screen.queryByText('Logout')
    expect(logout).toBeNull()
  })
})
