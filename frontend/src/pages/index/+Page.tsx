import { Formik, Form, Field, ErrorMessage } from 'formik'
import { useAuthContext } from '../../components/useAuthContext'
import { useState } from 'react'
import { ropeApi, type MoodleUser, type CourseBuild, type MoodleSettings, type SchoolDistrict } from '../../utils/ropeApi'
import styled from 'styled-components'
import * as Yup from 'yup'

const Wrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  margin-top: 50px;
`

const Label = styled.label`
  display: flex;
  align-items: center;
  width: 100%;
`

const Input = styled(Field)`
  margin-left: 10px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  flex-grow: 1;
`

const Select = styled(Field)`
  margin-left: 10px;
  padding: 8px;
  flex-grow: 1;
`

const StyledForm = styled(Form)`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background-color: #00504721;
  border: 1px solid #00504721;
  border-radius: 5px;
  padding: 1rem;
  align-items: center;
  min-width: 50%;
`

const StyledErrorMessage = styled(ErrorMessage)`
  color: red;
  margin: 0;
`

const BaseContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-around;
  min-width: 50%;
  background-color: #00504721;
  border: 1px solid #00504721;
  border-radius: 5px;
  padding: 1rem;
`

const CourseBuildResultsContainer = styled(BaseContainer)`
  gap: 1rem;
`

const InstructorSpan = styled.span`
  font-weight: 700;
`

const Button = styled.button`
  padding: 8px 16px;
  min-width: 25%;
`

const ErrorTag = styled.p`
  color: red;
`

const UserMessage = styled.p`
  color: grey;
`

interface CourseBuildFormValues {
  instructorFirstName: string
  instructorLastName: string
  instructorEmail: string
  schoolDistrictName: string
}

interface InstructorEmailValue {
  instructorEmail: string
}

function Page(): JSX.Element {
  const authContext = useAuthContext()

  const [settings, setSettings] = useState<MoodleSettings[]>([
    { name: 'academic_year', value: '' },
    { name: 'academic_year_short', value: '' },
    { name: 'course_category', value: '' },
    { name: 'base_course_id', value: '' }
  ])
  const [instructorEmail, setInstructorEmail] = useState<string>('')
  const [instructorMessage, setInstructorMessage] = useState<string>('')
  const [moodleUser, setMoodleUser] = useState<MoodleUser | null>(null)
  const [courseBuild, setCourseBuild] = useState<CourseBuild[] | null>(null)
  const [showCourseBuildForm, setShowCourseBuildForm] = useState<boolean>(false)
  const [courseBuildFormMessage, setCourseBuildFormMessage] = useState<string>('')
  const [districts, setDistricts] = useState<SchoolDistrict[]>([])
  const [dropdownDisabled, setDropdownDisabled] = useState<boolean>(false)

  const courseBuildFormSchema = Yup.object().shape({
    instructorFirstName: Yup.string().required('Instructor first name required'),
    instructorLastName: Yup.string().required('Instructor last name required'),
    instructorEmail: Yup.string().email('Invalid email').required('Instructor email required'),
    schoolDistrictName: Yup.string().required('A school district must be selected')
  })

  const instructorFormSchema = Yup.object().shape({
    instructorEmail: Yup.string().email('Invalid email').required('Instructor email required')
  })

  const fetchSettings = async (): Promise<void> => {
    try {
      const moodleSettings = await ropeApi.getMoodleSettings()
      setSettings(moodleSettings)
    } catch (error) {
      console.error('Error fetching moodle settings:', error)
    }
  }

  const fetchDistricts = async (): Promise<void> => {
    try {
      const districtsFromApi = await ropeApi.getDistricts()
      setDistricts(districtsFromApi)
    } catch (error) {
      console.error('Error fetching districts:', error)
    }
  }

  const clearCourseBuildFeedback = (): void => {
    setCourseBuildFormMessage('')
    setCourseBuild(null)
    setShowCourseBuildForm(false)
    setDropdownDisabled(false)
  }

  const handleUserMoodleSearch = async (values: InstructorEmailValue): Promise<void> => {
    try {
      clearCourseBuildFeedback()
      const user: MoodleUser = await ropeApi.getMoodleUser(values.instructorEmail)
      if (user == null) {
        setInstructorMessage('User with that email does not have a Moodle account')
        setMoodleUser(null)
        return
      }
      setInstructorEmail(values.instructorEmail)
      setInstructorMessage('')
      setMoodleUser(user)
      await fetchSettings()
    } catch (error) {
      console.error('Failed to retrieve instructor from Moodle:', error)
      setInstructorMessage('Failed to retrieve instructor from Moodle')
    }
  }

  const fetchCourseBuilds = async (): Promise<void> => {
    try {
      const academicYear = settings.find((setting) => setting.name === 'academic_year')
      if (academicYear !== undefined) {
        const courseBuilds: CourseBuild[] = await ropeApi.getCourseBuilds(academicYear.value, instructorEmail)
        if (courseBuilds.length > 0) {
          setShowCourseBuildForm(false)
          setCourseBuildFormMessage('')
          setCourseBuild(courseBuilds)
          return
        }
      }
      if (authContext.isAdmin || authContext.isManager) {
        await fetchDistricts()
        setShowCourseBuildForm(true)
      }
      setCourseBuildFormMessage('A course build does not exist for that instructor')
    } catch (error) {
      console.error('Error fetching course builds:', error)
    }
  }

  const handleCourseBuildFormSubmit = async (values: CourseBuildFormValues): Promise<void> => {
    try {
      await ropeApi.createCourseBuild(
        values.instructorFirstName,
        values.instructorLastName,
        values.instructorEmail,
        values.schoolDistrictName
      )
      setCourseBuildFormMessage('Course build successfully created!')
      setDropdownDisabled(true)
    } catch (error) {
      console.error('Failed to save course build settings')
      setCourseBuildFormMessage('Unable to create course build!')
    }
  }
  return (
    <Wrapper>
        <h2>Search for Moodle User</h2>
        <Formik
          initialValues={{ instructorEmail }}
          validationSchema={instructorFormSchema}
          onSubmit={handleUserMoodleSearch}
        >
          {({ values, isSubmitting, setFieldValue }) => (
            <StyledForm>
              <Label><InstructorSpan>Instructor Email:</InstructorSpan>
              <Input
                name='instructorEmail'
                type='email'
                placeholder='Enter instructor email'
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                  setInstructorMessage('')
                  void setFieldValue('instructorEmail',
                    e.target.value)
                }}
              />
              </Label>
              <StyledErrorMessage component='p' name='instructorEmail' />
              <Button type='submit' disabled={isSubmitting}>Submit</Button>
            </StyledForm>
          )}
        </Formik>
      {(instructorMessage.length > 0) && <ErrorTag>{instructorMessage}</ErrorTag>}
      <h2>Instructor Information</h2>
      {(moodleUser !== null) && <BaseContainer>
        <div>
          <p><InstructorSpan>First Name:</InstructorSpan> {moodleUser.firstName}</p>
          <p><InstructorSpan>Last Name:</InstructorSpan> {moodleUser.lastName}</p>
          <p><InstructorSpan>Email:</InstructorSpan> {moodleUser.email}</p>
        </div>
        <Button onClick={() => { void fetchCourseBuilds() }}>Find Course Build</Button>
      </BaseContainer>
        }
      <h2>Course Build Information</h2>
      {(courseBuild !== null) && <CourseBuildResultsContainer>
        <div>
          <p><InstructorSpan>Creator:</InstructorSpan> {courseBuild[0].creatorEmail}</p>
          <p><InstructorSpan>Status:</InstructorSpan> {courseBuild[0].status}</p>
          <p><InstructorSpan>Instructor First Name:</InstructorSpan> {courseBuild[0].instructorFirstName}</p>
          <p><InstructorSpan>Instructor Last Name:</InstructorSpan> {courseBuild[0].instructorLastName}</p>
          <p><InstructorSpan>Instructor Email:</InstructorSpan> {courseBuild[0].instructorEmail}</p>
        </div>
        <div>
          <p><InstructorSpan>School District:</InstructorSpan> {courseBuild[0].schoolDistrictName}</p>
          <p><InstructorSpan>Academic Year:</InstructorSpan> {courseBuild[0].academicYear}</p>
          <p><InstructorSpan>Academic Year Short:</InstructorSpan> {courseBuild[0].academicYearShort}</p>
          <p><InstructorSpan>Course Name:</InstructorSpan> {courseBuild[0].courseName}</p>
          <p><InstructorSpan>Course Short Name:</InstructorSpan> {courseBuild[0].courseShortName}</p>
        </div>
      </CourseBuildResultsContainer>}
      {(authContext.isManager || authContext.isAdmin) &&
        <>
          {(showCourseBuildForm && moodleUser !== null) &&
          <>
            <Formik
            initialValues={
              {
                instructorFirstName: moodleUser.firstName,
                instructorLastName: moodleUser.lastName,
                instructorEmail: moodleUser.email,
                schoolDistrictName: ''
              }
            }
            validationSchema={courseBuildFormSchema}
            onSubmit={handleCourseBuildFormSubmit}
            >
              {({ values, isSubmitting, setFieldValue }) => (
                <StyledForm>
                  <Label><InstructorSpan>Instructor First Name:</InstructorSpan>
                  <Input
                    name='instructorFirstName'
                    type='text'
                    placeholder='Enter instructor first name'
                    disabled={true}
                  />
                  </Label>
                  <StyledErrorMessage component='p' name='instructorFirstName' />
                  <Label><InstructorSpan>Instructor Last Name:</InstructorSpan>
                  <Input
                    name='instructorLastName'
                    type='text'
                    placeholder='Enter instructor last name'
                    disabled={true}
                  />
                  </Label>
                  <StyledErrorMessage component='p' name='instructorLastName' />
                  <Label><InstructorSpan>Instructor Email:</InstructorSpan>
                  <Input
                    name='instructorEmail'
                    type='email'
                    placeholder='Enter instructor email'
                    disabled={true}
                  />
                  </Label>
                  <StyledErrorMessage component='p' name='instructorEmail' />
                  <Label><InstructorSpan>School District Name:</InstructorSpan>
                  <Select
                    as='select'
                    name='schoolDistrictName'
                    disabled={isSubmitting || dropdownDisabled}
                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                      setCourseBuildFormMessage('')
                      void setFieldValue('schoolDistrictName',
                        e.target.value)
                    }}
                  >
                    <option value=''>Select a school district</option>
                    {districts.map((district) => (
                      <option key={district.name} value={district.name}>
                        {district.name}
                      </option>
                    ))}
                  </Select>
                  </Label>
                  <StyledErrorMessage component='p' name='schoolDistrictName' />
                  <Button type='submit' disabled={isSubmitting || dropdownDisabled}>Create Course Build</Button>
                </StyledForm>
              )}
            </Formik>
          </>}
        </>
      }
      {(courseBuildFormMessage.length > 0) && <UserMessage>{courseBuildFormMessage}</UserMessage>}
    </Wrapper>
  )
}
export { Page }
