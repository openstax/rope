import { useState, useEffect } from 'react'
import DataTable, { type TableColumn } from 'react-data-table-component'
import { ropeApi, type CourseBuild } from '../../utils/ropeApi'
import { styled } from 'styled-components'

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
  padding: 8px
`
const FiltersContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  
  span {
    margin: 8px;
  }
  input {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 5px;
    maxwidth: 200px;

    &:focus {
      outline: none;
      border-color: #007bff;
    }
  }
`

function Page(): JSX.Element {
  const [courseBuilds, setCourseBuilds] = useState<CourseBuild[]>([])
  const [filteredData, setFilteredData] = useState<CourseBuild[]>([])
  const [filters, setFilters] = useState<{ email: string, academicYear: string }>({
    email: '',
    academicYear: ''
  })

  useEffect(() => {
    void fetchData()
  }, [])

  const fetchData = async (): Promise<void> => {
    try {
      const data = await ropeApi.getAllCourseBuilds()
      setCourseBuilds(data)
    } catch (error) {
      console.error('Error fetching course builds:', error)
    }
  }

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target
    setFilters({ ...filters, [name]: value })
  }

  useEffect(() => {
    let filteredResults = courseBuilds

    if (filters.email !== '') {
      filteredResults = filteredResults.filter(
        (build) => build.instructorEmail.toLowerCase().includes(filters.email.toLowerCase())
      )
    }

    if (filters.academicYear !== '') {
      filteredResults = filteredResults.filter(
        (build) => build.academicYear.toLowerCase().includes(filters.academicYear.toLowerCase())
      )
    }

    setFilteredData(filteredResults)
  }, [filters, courseBuilds])

  const columns: Array<TableColumn<CourseBuild>> = [
    {
      name: 'Instructor Name',
      selector: row => `${row.instructorFirstName} ${row.instructorLastName}`,
      sortable: true,
      wrap: true
    },
    {
      name: 'Instructor Email',
      selector: row => row.instructorEmail,
      sortable: true,
      wrap: true
    },
    {
      name: 'School District Name',
      selector: row => row.schoolDistrictName,
      sortable: true,
      wrap: true
    },
    {
      name: 'Academic Year',
      selector: row => row.academicYear,
      wrap: true
    },
    {
      name: 'Course Name',
      selector: row => row.courseName,
      grow: 2,
      wrap: true
    },
    {
      name: 'Course ID',
      selector: row => row.courseId ?? '',
      sortable: true,
      wrap: true
    },
    {
      name: 'Course Enrollment Url',
      selector: row => row.courseEnrollmentUrl ?? '',
      wrap: true
    },
    {
      name: 'Course Enrollment Key',
      selector: row => row.courseEnrollmentKey ?? '',
      wrap: true
    },
    {
      name: 'Status',
      selector: row => row.status,
      wrap: true
    },
    {
      name: 'Creator Email',
      selector: row => row.creatorEmail,
      wrap: true
    }
  ]

  return (
    <Container>
      <Title>Courses</Title>
      <FiltersContainer>
        <span>Email Filter </span>
        <input
          type="text"
          name="email"
          placeholder="Filter by Email"
          value={filters.email}
          onChange={handleFilterChange}
        />
        <span>Academic Year Filter </span>
        <input
          type="text"
          name="academicYear"
          placeholder="Filter by Academic Year"
          value={filters.academicYear}
          onChange={handleFilterChange}
        />
      </FiltersContainer>
      <DataTable
        columns={columns}
        data={filteredData}
        defaultSortFieldId={6}
        defaultSortAsc={false}
        pagination
        highlightOnHover
        striped
      />
            </Container>

  )
}

export { Page }
