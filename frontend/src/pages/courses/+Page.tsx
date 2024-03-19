import { useState, useEffect, useMemo } from 'react'
import DataTable from 'react-data-table-component'
import { ropeApi, type CourseBuild } from '../../utils/ropeApi'
import styled from 'styled-components'
function Page(): JSX.Element {
  const Title = styled.h2`
  color: #333;
  text-align: center;
  margin-bottom: 20px;
`
  const Container = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  margin-top: 50px;
`

  const [filterText, setFilterText] = useState('')
  const [activeAcademicYear, setActiveAcademicYear] = useState<string | null>(null)
  const [courses, setCourses] = useState<CourseBuild[]>([])

  useEffect(() => {
    const fetchSettings = async (): Promise<void> => {
      try {
        const settings = await ropeApi.getMoodleSettings()
        const activeAYSetting = settings.find(setting => setting.name === 'academic_year')
        if ((activeAYSetting?.value) != null) {
          setActiveAcademicYear(activeAYSetting.value)
        }
      } catch (error) {
        console.error('Failed to fetch Moodle settings:', error)
      }
    }

    void fetchSettings()
  }, [])

  useEffect(() => {
    void fetchCourses()
  }, [])

  const fetchCourses = async (academicYear?: string, instructorEmail?: string): Promise<void> => {
    try {
      const courseBuilds = await ropeApi.fakeGetCourseBuilds()
      console.log(courseBuilds)
      setCourses(courseBuilds)
    } catch (error) {
      console.error('Failed to fetch courses:', error)
      setCourses([])
    }
  }

  const filteredItems = courses.filter(item => {
    const matchesEmail = item.instructor_email.includes(filterText)
    const isInActiveYear = item.academic_year === activeAcademicYear
    return matchesEmail && isInActiveYear
  })
  const columns = useMemo(() => [
    {
      name: 'Instructor Name',
      selector: row => `${row.instructor_firstname} ${row.instructor_lastname}`,
      sortable: true
    },
    {
      name: 'Email',
      selector: row => row.instructor_email,
      sortable: true
    },
    {
      name: 'Course Name',
      selector: row => row.course_name,
      sortable: true
    },
    {
      name: 'Academic Year',
      selector: row => row.academic_year,
      sortable: true
    }
  ], [])

  const subHeaderComponentMemo = useMemo(() => {
    const handleClear = (): void => {
      if (filterText.length > 0) {
        setFilterText('')
      }
    }

    return (
      <div>
        Filter:
        <input
          id="search"
          type="text"
          placeholder="Filter By Email"
          aria-label="Search Input"
          value={filterText}
          onChange={e => { setFilterText(e.target.value) }}
        />
        <button onClick={handleClear}>Clear</button>
      </div>
    )
  }, [filterText])

  return (
    <Container>
      <Title>Courses</Title>

    <DataTable
      columns={columns}
      data={filteredItems}
      pagination
      subHeader
      subHeaderComponent={subHeaderComponentMemo}
      persistTableHead
    />
    </Container>
  )
}
export { Page }
