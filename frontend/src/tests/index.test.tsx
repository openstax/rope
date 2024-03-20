import { render, screen, fireEvent, act } from '@testing-library/react'
import { expect, vi, afterEach } from 'vitest'
import { Page } from '../pages/index/+Page'
import { type PageContext } from 'vike/types'
import { AuthContext, AuthStatus } from '../components/useAuthContext'
import { PageContextProvider } from '../components/usePageContext'

const createFetchResponse = (data: unknown): unknown => {
  return {
    ok: true,
    json: async () => await Promise.resolve(data)
  }
}

describe('Index page', async () => {
  afterEach(() => {
    vi.resetAllMocks()
  })

  it('verified user, manager, or admin fetches an existing course build', async () => {
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

    global.fetch = vi.fn()
      .mockResolvedValueOnce(createFetchResponse(mockMoodleUser))
      .mockResolvedValueOnce(createFetchResponse(mockMoodleSettings))
      .mockResolvedValueOnce(createFetchResponse(mockCourseBuild))

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
    await act(async () => {
      fireEvent.change(emailInput, { target: { value: 'fsaint@snowfallisd.edu' } })
      fireEvent.click(screen.getByText('Submit'))
    })

    await screen.findByText('First Name:')
    expect(await screen.findByText('Franklin'))
    fireEvent.click(screen.getByText('Find Course Build'))

    await screen.findByText('School District:')
    expect(await screen.findByText('snowfall_isd'))
    expect(global.fetch).toHaveBeenNthCalledWith(1, '/api/moodle/user?email=fsaint@snowfallisd.edu')
    expect(global.fetch).toHaveBeenNthCalledWith(2, '/api/admin/settings/moodle')
    expect(global.fetch).toHaveBeenNthCalledWith(3, '/api/moodle/course/build?academic_year=AY 2040&instructor_email=fsaint@snowfallisd.edu')
  })

  it('verified user, manager, or admin receive error message when submitting empty instructor email to moodle', async () => {
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

    await act(async () => {
      fireEvent.click(screen.getByText('Submit'))
    })
    expect(screen.findByText('Instructor email required'))
  })

  it('verified user, manager, or admin receive error message when submitting an email address that does not exist in moodle', async () => {
    const mockMoodleUser = null

    global.fetch = vi.fn().mockResolvedValueOnce(createFetchResponse(mockMoodleUser))

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
    await act(async () => {
      fireEvent.change(emailInput, { target: { value: 'lsimmons@email.edu' } })
      fireEvent.click(screen.getByText('Submit'))
    })
    expect(global.fetch).toHaveBeenCalledWith('/api/moodle/user?email=lsimmons@email.edu')
    expect(screen.findByText('User with that email does not have a Moodle account'))
  })

  it('verified user fetches a non-existing course build', async () => {
    const mockMoodleUser = { first_name: 'Gustavo', last_name: 'Zapata', email: 'gzapata@snowfallisd.edu' }
    const mockMoodleSettings = [
      { name: 'academic_year', value: 'AY 2040' },
      { name: 'course_category', value: '1' },
      { name: 'academic_year_short', value: 'AY40' },
      { name: 'base_course_id', value: '21' }
    ]
    const mockCourseBuild: [] = []

    global.fetch = vi.fn()
      .mockResolvedValueOnce(createFetchResponse(mockMoodleUser))
      .mockResolvedValueOnce(createFetchResponse(mockMoodleSettings))
      .mockResolvedValueOnce(createFetchResponse(mockCourseBuild))

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
    await act(async () => {
      fireEvent.change(emailInput, { target: { value: 'gzapata@snowfallisd.edu' } })
      fireEvent.click(screen.getByText('Submit'))
    })

    await screen.findByText('First Name:')
    expect(await screen.findByText('Gustavo'))
    fireEvent.click(screen.getByText('Find Course Build'))

    expect(await screen.findByText('A course build does not exist for that instructor'))
    expect(global.fetch).toHaveBeenNthCalledWith(1, '/api/moodle/user?email=gzapata@snowfallisd.edu')
    expect(global.fetch).toHaveBeenNthCalledWith(2, '/api/admin/settings/moodle')
    expect(global.fetch).toHaveBeenNthCalledWith(3, '/api/moodle/course/build?academic_year=AY 2040&instructor_email=gzapata@snowfallisd.edu')
  })

  it('manager creates a new course build', async () => {
    const mockMoodleUser = { first_name: 'Reed', last_name: 'Thompson', email: 'rthompson@snowfallisd.edu' }
    const mockMoodleSettings = [
      { name: 'academic_year', value: 'AY 2040' },
      { name: 'course_category', value: '1' },
      { name: 'academic_year_short', value: 'AY40' },
      { name: 'base_course_id', value: '21' }
    ]
    const mockCourseBuild: [] = []
    const mockDistrict = [
      { name: 'snowfall_isd', active: true }
    ]
    const mockCreateCourseBuild = {
      instructor_firstname: 'Reed',
      instructor_lastname: 'Thompson',
      instructor_email: 'rthompson@snowfallisd.edu',
      school_district_name: 'snowfall_isd'
    }
    const mockNewCourseBuild = [{
      instructor_firstname: 'Reed',
      instructor_lastname: 'Thompson',
      instructor_email: 'rthompson@snowfallisd.edu',
      school_district_name: 'snowfall_isd',
      academic_year: 'AY 2040',
      academic_year_short: 'AY40',
      course_name: 'Algebra 1 - Reed Thompson (AY 2040)',
      course_shortname: 'Alg1 RT AY40',
      creator_email: 'admin@rice.edu',
      status: 'created'
    }]

    global.fetch = vi.fn()
      .mockResolvedValueOnce(createFetchResponse(mockMoodleUser))
      .mockResolvedValueOnce(createFetchResponse(mockMoodleSettings))
      .mockResolvedValueOnce(createFetchResponse(mockCourseBuild))
      .mockResolvedValueOnce(createFetchResponse(mockDistrict))
      .mockResolvedValueOnce(createFetchResponse(mockCreateCourseBuild))
      .mockResolvedValueOnce(createFetchResponse(mockNewCourseBuild))

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/'
    } as PageContext

    render(
    <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: false, isManager: true, email: 'manager@rice.edu' }}>
            <Page />
        </AuthContext.Provider>
    </PageContextProvider>
    )

    const emailInput = screen.getByLabelText('Instructor Email:')
    await act(async () => {
      fireEvent.change(emailInput, { target: { value: 'rthompson@snowfallisd.edu' } })
      fireEvent.click(screen.getByText('Submit'))
    })

    await screen.findByText('First Name:')
    expect(await screen.findByText('Reed'))
    fireEvent.click(screen.getByText('Find Course Build'))

    await screen.findByText('Instructor First Name:')
    const instructorFirstName = screen.getByLabelText('Instructor First Name:')
    const instructorLastName = screen.getByLabelText('Instructor Last Name:')
    const instructorEmail = screen.getAllByLabelText('Instructor Email:')[1]

    await screen.findByText('A course build does not exist for that instructor')
    await act(async () => {
      fireEvent.change(instructorFirstName, { target: { value: 'Reed' } })
      fireEvent.change(instructorLastName, { target: { value: 'Thompson' } })
      fireEvent.change(instructorEmail, { target: { value: 'rthompson@snowfallisd.edu' } })
      fireEvent.change(screen.getByRole('combobox'), { target: { value: 'snowfall_isd' } })
      fireEvent.click(screen.getByText('Create Course Build'))
    })
    expect(await screen.findByText('Course build successfully created!'))

    fireEvent.click(screen.getByText('Find Course Build'))

    await screen.findByText('Course Name:')
    expect(await screen.findByText('Algebra 1 - Reed Thompson (AY 2040)'))

    expect(global.fetch).toHaveBeenNthCalledWith(1, '/api/moodle/user?email=rthompson@snowfallisd.edu')
    expect(global.fetch).toHaveBeenNthCalledWith(2, '/api/admin/settings/moodle')
    expect(global.fetch).toHaveBeenNthCalledWith(3, '/api/moodle/course/build?academic_year=AY 2040&instructor_email=rthompson@snowfallisd.edu')
    expect(global.fetch).toHaveBeenNthCalledWith(4, '/api/admin/settings/district')
    expect(global.fetch).toHaveBeenNthCalledWith(5, '/api/moodle/course/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(mockCreateCourseBuild)
    })
    expect(global.fetch).toHaveBeenNthCalledWith(6, '/api/moodle/course/build?academic_year=AY 2040&instructor_email=rthompson@snowfallisd.edu')
  })

  it('admin creates a new course build', async () => {
    const mockMoodleUser = { first_name: 'Avi', last_name: 'Drexler', email: 'adrexler@snowfallisd.edu' }
    const mockMoodleSettings = [
      { name: 'academic_year', value: 'AY 2040' },
      { name: 'course_category', value: '1' },
      { name: 'academic_year_short', value: 'AY40' },
      { name: 'base_course_id', value: '21' }
    ]
    const mockCourseBuild: [] = []
    const mockDistrict = [
      { name: 'snowfall_isd', active: true }
    ]
    const mockCreateCourseBuild = {
      instructor_firstname: 'Avi',
      instructor_lastname: 'Drexler',
      instructor_email: 'adrexler@snowfallisd.edu',
      school_district_name: 'snowfall_isd'
    }
    const mockNewCourseBuild = [{
      instructor_firstname: 'Avi',
      instructor_lastname: 'Drexler',
      instructor_email: 'adrexler@snowfallisd.edu',
      school_district_name: 'snowfall_isd',
      academic_year: 'AY 2040',
      academic_year_short: 'AY40',
      course_name: 'Algebra 1 - Avi Drexler (AY 2040)',
      course_shortname: 'Alg1 AD AY40',
      creator_email: 'admin@rice.edu',
      status: 'created'
    }]

    global.fetch = vi.fn()
      .mockResolvedValueOnce(createFetchResponse(mockMoodleUser))
      .mockResolvedValueOnce(createFetchResponse(mockMoodleSettings))
      .mockResolvedValueOnce(createFetchResponse(mockCourseBuild))
      .mockResolvedValueOnce(createFetchResponse(mockDistrict))
      .mockResolvedValueOnce(createFetchResponse(mockCreateCourseBuild))
      .mockResolvedValueOnce(createFetchResponse(mockNewCourseBuild))

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/'
    } as PageContext

    render(
    <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'admin@rice.edu' }}>
            <Page />
        </AuthContext.Provider>
    </PageContextProvider>
    )

    const emailInput = screen.getByLabelText('Instructor Email:')
    await act(async () => {
      fireEvent.change(emailInput, { target: { value: 'adrexler@snowfallisd.edu' } })
      fireEvent.click(screen.getByText('Submit'))
    })

    await screen.findByText('First Name:')
    expect(await screen.findByText('Avi'))
    fireEvent.click(screen.getByText('Find Course Build'))

    await screen.findByText('Instructor First Name:')
    const instructorFirstName = screen.getByLabelText('Instructor First Name:')
    const instructorLastName = screen.getByLabelText('Instructor Last Name:')
    const instructorEmail = screen.getAllByLabelText('Instructor Email:')[1]

    await screen.findByText('A course build does not exist for that instructor')
    await act(async () => {
      fireEvent.change(instructorFirstName, { target: { value: 'Avi' } })
      fireEvent.change(instructorLastName, { target: { value: 'Drexler' } })
      fireEvent.change(instructorEmail, { target: { value: 'adrexler@snowfallisd.edu' } })
      fireEvent.change(screen.getByRole('combobox'), { target: { value: 'snowfall_isd' } })
      fireEvent.click(screen.getByText('Create Course Build'))
    })
    await screen.findByText('Course build successfully created!')

    fireEvent.click(screen.getByText('Find Course Build'))

    await screen.findByText('Course Name:')
    expect(await screen.findByText('Algebra 1 - Avi Drexler (AY 2040)'))

    expect(global.fetch).toHaveBeenNthCalledWith(1, '/api/moodle/user?email=adrexler@snowfallisd.edu')
    expect(global.fetch).toHaveBeenNthCalledWith(2, '/api/admin/settings/moodle')
    expect(global.fetch).toHaveBeenNthCalledWith(3, '/api/moodle/course/build?academic_year=AY 2040&instructor_email=adrexler@snowfallisd.edu')
    expect(global.fetch).toHaveBeenNthCalledWith(4, '/api/admin/settings/district')
    expect(global.fetch).toHaveBeenNthCalledWith(5, '/api/moodle/course/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(mockCreateCourseBuild)
    })
    expect(global.fetch).toHaveBeenNthCalledWith(6, '/api/moodle/course/build?academic_year=AY 2040&instructor_email=adrexler@snowfallisd.edu')
  })
})
