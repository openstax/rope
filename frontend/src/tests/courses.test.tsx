import { render, screen, fireEvent } from '@testing-library/react'
import { expect, vi } from 'vitest'
import { Page } from '../pages/courses/+Page'
import { type PageContext } from 'vike/types'
import { AuthContext, AuthStatus } from '../components/useAuthContext'
import { PageContextProvider } from '../components/usePageContext'

const mockCourseBuilds = [{
  instructor_firstname: 'Avi',
  instructor_lastname: 'Drexler',
  instructor_email: 'adrexler@snowfallisd.edu',
  school_district_name: 'snowfall_isd',
  academic_year: 'AY 2040',
  academic_year_short: 'AY40',
  course_name: 'Algebra 1 - Avi Drexler (AY 2040)',
  course_shortname: 'Alg1 AD AY40',
  creator_email: 'admin@rice.edu',
  status: 'created',
  course_id: '37',
  course_enrollment_url: 'enrollment_url1',
  course_enrollment_key: 'key1'
},
{
  instructor_firstname: 'Prabhdip',
  instructor_lastname: 'Gill',
  instructor_email: 'prabhdip@rice.edu',
  school_district_name: 'snowfall_isd',
  academic_year: 'AY 2039',
  academic_year_short: 'AY39',
  course_name: 'Algebra 1 - Prabhdip Gill (AY 2039)',
  course_shortname: 'Alg1 PG AY39',
  creator_email: 'admin@rice.edu',
  status: 'created',
  course_id: '47',
  course_enrollment_url: 'enrollment_url2',
  course_enrollment_key: 'key2'

},
{
  instructor_firstname: 'Prabhdip',
  instructor_lastname: 'Gill',
  instructor_email: 'prabhdip@rice.edu',
  school_district_name: 'woodcreek',
  academic_year: 'AY 2040',
  academic_year_short: 'AY40',
  course_name: 'Algebra 1 - Prabhdip Gill (AY 2040)',
  course_shortname: 'Alg1 PG AY40',
  creator_email: 'admin@rice.edu',
  status: 'created',
  course_id: '57',
  course_enrollment_url: 'enrollment_url3',
  course_enrollment_key: 'key3'
}]

describe('Courses page', async () => {
  it('fetches and displays course builds from API', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => await Promise.resolve(mockCourseBuilds)
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/courses'
    } as PageContext

    render(
          <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'rice@rice.edu' }}>
          <Page>
          </Page>
        </AuthContext.Provider>
        </PageContextProvider>
    )

    expect(global.fetch).toHaveBeenCalledWith('/api/moodle/course/build')
    await screen.findByText('Algebra 1 - Avi Drexler (AY 2040)')
    expect(screen.getAllByText('Prabhdip Gill').length).toBe(2)
    expect(screen.getAllByText('prabhdip@rice.edu').length).toBe(2)
    expect(screen.queryByText('AY 2039')).toBeInTheDocument()
    expect(screen.queryByText('Algebra 1 - Prabhdip Gill (AY 2039)')).toBeInTheDocument()
    expect(screen.queryByText('37')).toBeInTheDocument()
    expect(screen.queryByText('enrollment_url1')).toBeInTheDocument()
    expect(screen.queryByText('key1')).toBeInTheDocument()
  })
  it('Filters by email and academic year', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => await Promise.resolve(mockCourseBuilds)
    })

    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    const pageContext = {
      urlPathname: '/courses'
    } as PageContext

    render(
          <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={{ status: AuthStatus.SignedIn, isAdmin: true, isManager: false, email: 'rice@rice.edu' }}>
          <Page>
          </Page>
        </AuthContext.Provider>
        </PageContextProvider>
    )

    expect(global.fetch).toHaveBeenCalledWith('/api/moodle/course/build')
    await screen.findByText('Avi Drexler')

    fireEvent.change(screen.getByPlaceholderText('Filter by Email'), { target: { value: 'prabhdip@rice.edu' } })
    fireEvent.change(screen.getByPlaceholderText('Filter by Academic Year'), { target: { value: 'AY 2040' } })

    expect(screen.queryByText('Avi Drexler')).not.toBeInTheDocument()
    expect(screen.queryByText('Prabhdip Gill')).toBeInTheDocument()
    expect(screen.getAllByText('prabhdip@rice.edu').length).toBe(1)
    expect(screen.queryByText('woodcreek')).toBeInTheDocument()
    expect(screen.queryByText('AY 2039')).not.toBeInTheDocument()
    expect(screen.queryByText('Algebra 1 - Prabhdip Gill (AY 2039)')).not.toBeInTheDocument()
    expect(screen.queryByText('Algebra 1 - Avi Drexler (AY 2040)')).not.toBeInTheDocument()
    expect(screen.queryByText('created')).toBeInTheDocument()
    expect(screen.queryByText('57')).toBeInTheDocument()
    expect(screen.queryByText('enrollment_url3')).toBeInTheDocument()
    expect(screen.queryByText('key3')).toBeInTheDocument()
  })
})
