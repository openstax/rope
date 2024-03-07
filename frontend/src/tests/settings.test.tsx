import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { expect, vi } from 'vitest'
import { Page } from '../pages/settings/+Page'
import { type PageContext } from 'vike/types'
import { AuthContext, AuthStatus } from '../components/useAuthContext'
import { PageContextProvider } from '../components/usePageContext'

describe('Settings page', async () => {
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

  it('fetches settings and districts when admin is logged in', async () => {
    const mockSettings = [
      { id: 1, name: 'academic_year', value: '2024' },
      { id: 2, name: 'course_category', value: 'Math' },
      { id: 3, name: 'academic_year_short', value: 'short' },
      { id: 4, name: 'base_course_id', value: '42' }
    ]
    const mockDistricts = [
      { id: 1, name: 'District 1', active: true },
      { id: 2, name: 'District 2', active: false }
    ]

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve(mockSettings)
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve(mockDistricts)
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/settings'
    } as PageContext

    render(
      <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'admin@rice.edu' }}>
          <Page />
        </AuthContext.Provider>
      </PageContextProvider>
    )

    await screen.findByDisplayValue('2024')
    await screen.findByText('District 1')
    expect(global.fetch).toHaveBeenNthCalledWith(1, '/api/admin/settings/moodle')
    expect(global.fetch).toHaveBeenNthCalledWith(2, '/api/admin/settings/district')

    await screen.findByDisplayValue('2024')
    await screen.findByDisplayValue('Math')
    await screen.findByDisplayValue('short')
    await screen.findByDisplayValue('42')

    expect(screen.getByText('District 1')).toBeInTheDocument()
    expect(screen.getByText('District 2')).toBeInTheDocument()
    expect(screen.getByText('Active: Yes')).toBeInTheDocument()
    expect(screen.getByText('Active: No')).toBeInTheDocument()
  })
  it('updates Moodle settings when form is submitted', async () => {
    const mockSettings = [
      { id: 1, name: 'academic_year', value: '2024' },
      { id: 2, name: 'course_category', value: 'Math' },
      { id: 3, name: 'academic_year_short', value: 'short' },
      { id: 4, name: 'base_course_id', value: '42' }
    ]
    const mockDistricts = [
      { id: 1, name: 'District 1', active: true },
      { id: 2, name: 'District 2', active: false }
    ]

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve(mockSettings)
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve(mockDistricts)
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve({ name: 'academic_year', value: '2025', id: 1 })
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve({ id: 2, name: 'course_category', value: 'Math' })
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve({ id: 3, name: 'academic_year_short', value: 'short' })
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve({ id: 4, name: 'base_course_id', value: '42' })
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/settings'
    } as PageContext

    render(
      <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'admin@rice.edu' }}>
          <Page />
        </AuthContext.Provider>
      </PageContextProvider>
    )

    await screen.findByDisplayValue('2024')
    await screen.findByText('District 1')
    const academicYearInput = screen.getByPlaceholderText('academic_year')
    fireEvent.change(academicYearInput, { target: { value: '2025' } })
    fireEvent.click(screen.getByText('Save Settings'))
    await waitFor(() => {
      expect(global.fetch).toHaveBeenNthCalledWith(1, '/api/admin/settings/moodle')
      expect(global.fetch).toHaveBeenNthCalledWith(2, '/api/admin/settings/district')
      expect(global.fetch).toHaveBeenNthCalledWith(3, '/api/admin/settings/moodle/1', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'academic_year', value: '2025', id: 1 })
      })
    })
  })

  it('Add district', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => await Promise.resolve({ id: 0, name: 'New District', active: true })
    })
    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/settings'
    } as PageContext

    render(
      <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'admin@rice.edu' }}>
          <Page />
        </AuthContext.Provider>
      </PageContextProvider>
    )
    expect(screen.queryByText('New District')).not.toBeInTheDocument()

    const academicYearInput = screen.getByPlaceholderText('Enter district name')
    fireEvent.change(academicYearInput, { target: { value: 'New District' } })
    fireEvent.click(screen.getByText('Add District'))

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/admin/settings/district', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'New District', active: true, id: 0 })
      })
    })
  })

  it('changes district active state when toggle button is clicked', async () => {
    const mockDistricts = [{ id: 2, name: 'Example District', active: true }]
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => await Promise.resolve(mockDistricts)
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/settings'
    } as PageContext

    render(
      <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'admin@rice.edu' }}>
          <Page />
        </AuthContext.Provider>
      </PageContextProvider>
    )
    await screen.findByText('Active: Yes')
    await screen.findByText('Example District')

    fireEvent.click(screen.getByText('Toggle Active'))
    await screen.findByText('Active: No')

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/admin/settings/district/2', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: 2, active: false, name: 'Example District' })
      })
    })
  })
})
