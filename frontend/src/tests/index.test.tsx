import { render, screen, fireEvent } from '@testing-library/react'
import { expect, vi } from 'vitest'
import { Page } from '../pages/index/+Page'
import { type PageContext } from 'vike/types'
import { AuthContext, AuthStatus } from '../components/useAuthContext'
import { PageContextProvider } from '../components/usePageContext'

describe('Index page', async () => {
  it('verified user fetches an existing course build', async () => {
    const mockMoodleUser = { first_name: 'Franklin', last_name: 'Saint', email: 'fsaint@snowfallisd.edu' }
    const mockMoodleSettings = [
      { name: 'academic_year', value: 'AY 2040' },
      { name: 'course_category', value: '1' },
      { name: 'academic_year_short', value: 'AY40' },
      { name: 'base_course_id', value: '21' }
    ]
    const mockCourseBuild = [{
      instructor_firstname: 'Franklin',
      instructor_lastname: 'Saint',
      instructor_email: 'fsaint@snowfallisd.edu',
      school_district_name: 'snowfall_isd',
      academic_year: 'AY 2040',
      academic_year_short: 'AY40',
      course_name: 'Algebra 1 - Franklin Saint (AY 2040)',
      course_shortname: 'Alg1 FS AY40',
      creator_email: 'admin@rice.edu',
      status: 'created'
    }]

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve(mockMoodleUser)
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve(mockMoodleSettings)
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve(mockCourseBuild)
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/'
    } as PageContext

    render(
    <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: false, isManager: false, email: 'verifieduser@rice.edu' }}>
            <Page />
        </AuthContext.Provider>
    </PageContextProvider>
    )

    const emailInput = screen.getByLabelText('Instructor Email:')
    fireEvent.change(emailInput, { target: { value: 'fsaint@snowfallisd.edu' } })
    fireEvent.click(screen.getByText('Submit'))

    await screen.findByText('First Name:')
    expect(await screen.findByText('Franklin'))
    fireEvent.click(screen.getByText('Find Course Build'))

    await screen.findByText('School District:')
    expect(await screen.findByText('snowfall_isd'))
    expect(global.fetch).toHaveBeenCalledWith('/api/moodle/user?email=fsaint@snowfallisd.edu')
    expect(global.fetch).toHaveBeenCalledWith('/api/admin/settings/moodle')
    expect(global.fetch).toHaveBeenCalledWith('/api/moodle/course/build?academic_year=AY 2040&instructor_email=fsaint@snowfallisd.edu')
  })

  it('verified user fetches a non-existing course build', async () => {
    const mockMoodleUser = { first_name: 'Franklin', last_name: 'Saint', email: 'fsaint@snowfallisd.edu' }
    const mockMoodleSettings = [
      { name: 'academic_year', value: 'AY 2040' },
      { name: 'course_category', value: '1' },
      { name: 'academic_year_short', value: 'AY40' },
      { name: 'base_course_id', value: '21' }
    ]
    const mockCourseBuild: [] = []

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve(mockMoodleUser)
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve(mockMoodleSettings)
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => await Promise.resolve(mockCourseBuild)
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/'
    } as PageContext

    render(
    <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: false, isManager: false, email: 'verifieduser@rice.edu' }}>
            <Page />
        </AuthContext.Provider>
    </PageContextProvider>
    )

    const emailInput = screen.getByLabelText('Instructor Email:')
    fireEvent.change(emailInput, { target: { value: 'fsaint@snowfallisd.edu' } })
    fireEvent.click(screen.getByText('Submit'))

    await screen.findByText('First Name:')
    expect(await screen.findByText('Franklin'))
    fireEvent.click(screen.getByText('Find Course Build'))

    expect(await screen.findByText('A course build does not exist for that instructor'))
    expect(global.fetch).toHaveBeenCalledWith('/api/moodle/user?email=fsaint@snowfallisd.edu')
    expect(global.fetch).toHaveBeenCalledWith('/api/admin/settings/moodle')
    expect(global.fetch).toHaveBeenCalledWith('/api/moodle/course/build?academic_year=AY 2040&instructor_email=fsaint@snowfallisd.edu')
  })
})
