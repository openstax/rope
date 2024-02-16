import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { expect, vi } from 'vitest'
import { Page } from '../pages/users/+Page'
import { type PageContext } from 'vike/types'
import { AuthContext, AuthStatus } from '../components/useAuthContext'
import { PageContextProvider } from '../components/usePageContext'

describe('Users page', async () => {
  it('User is not admin', () => {
    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/users'
    } as PageContext

    render(
          <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: false, isManager: false, email: 'rice@rice.edu' }}>
          <Page>
          </Page>
        </AuthContext.Provider>
        </PageContextProvider>
    )
    const pageTitle = screen.getByText('This page is admin only')
    expect(pageTitle).toBeInTheDocument()
  })
  it('fetches users when admin is logged in', async () => {
    const mockUsers = [
      { id: 1, email: 'user1@rice.edu', is_admin: true, is_manager: false },
      { id: 2, email: 'user2@rice.edu', is_admin: false, is_manager: true }
    ]
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => await Promise.resolve(mockUsers)
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/users'
    } as PageContext

    render(
        <PageContextProvider pageContext={pageContext}>
          <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'admin@rice.edu' }}>
            <Page />
          </AuthContext.Provider>
        </PageContextProvider>
    )

    // Wait for fetchUsers to be called
    await screen.findByText('user1@rice.edu')
    expect(global.fetch).toHaveBeenCalledWith('/api/user')
    expect(screen.getByText('user1@rice.edu')).toBeInTheDocument()
    expect(screen.getByText('user2@rice.edu')).toBeInTheDocument()
  })

  it('adds a user when addUser is called', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve([{ id: 3, email: 'user3@rice.edu', is_admin: false, is_manager: false }])
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/users'
    } as PageContext

    render(
      <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'admin@rice.edu' }}>
          <Page />
        </AuthContext.Provider>
      </PageContextProvider>
    )
    const emailInput = screen.getByRole('textbox')
    fireEvent.change(emailInput, { target: { value: 'user3@rice.edu' } })
    fireEvent.click(screen.getByText('Add User'))
    expect(global.fetch).toHaveBeenCalledWith('/api/user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'user3@rice.edu', is_admin: false, is_manager: false })
    })
  })
  it('deletes a user when deleteUser is called', async () => {
    const mockUsers = [
      { id: 1, email: 'user1@example.com', is_admin: true, is_manager: false },
      { id: 2, email: 'user2@example.com', is_admin: false, is_manager: true }
    ]
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => await Promise.resolve(mockUsers)
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/users'
    } as PageContext

    render(
        <PageContextProvider pageContext={pageContext}>
          <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'admin@rice.edu' }}>
            <Page />
          </AuthContext.Provider>
        </PageContextProvider>
    )

    await screen.findByText('user1@example.com')
    expect(screen.getByText('user1@example.com')).toBeInTheDocument()
    expect(screen.getByText('user2@example.com')).toBeInTheDocument()

    global.fetch = vi.fn().mockImplementationOnce(async () =>
      await Promise.resolve({
        ok: true
      })
    )
    expect(screen.queryByText('user1@example.com')).toBeInTheDocument()

    fireEvent.click(screen.getAllByText('Remove user')[0])

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/user/1', { method: 'DELETE' })
    })

    expect(screen.queryByText('user1@example.com')).not.toBeInTheDocument()
  })

  it('updates user permissions when updateUserPermissions is called', async () => {
    const mockUsers = [
      { id: 1, email: 'user1@example.com', is_admin: true, is_manager: false },
      { id: 2, email: 'user2@example.com', is_admin: false, is_manager: true }
    ]
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => await Promise.resolve(mockUsers)
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/users'
    } as PageContext

    render(
        <PageContextProvider pageContext={pageContext}>
          <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'admin@rice.edu' }}>
            <Page />
          </AuthContext.Provider>
        </PageContextProvider>
    )

    await screen.findByText('user1@example.com')
    expect(screen.getByText('user1@example.com')).toBeInTheDocument()
    expect(screen.getByText('user2@example.com')).toBeInTheDocument()

    global.fetch = vi.fn().mockImplementationOnce(async () =>
      await Promise.resolve({
        ok: true
      })
    )

    const isAdminCheckbox = screen.getAllByRole('checkbox')[0]
    fireEvent.click(isAdminCheckbox)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/user/1', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: 1, is_admin: false, is_manager: false, email: 'user1@example.com' })
      })
    })
  })
})
