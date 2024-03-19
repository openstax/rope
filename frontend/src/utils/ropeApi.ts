export interface User {
  email: string
  isAdmin: boolean
  isManager: boolean
  id: number
}

export interface MoodleSettings {
  id?: number
  name: string
  value: string
}

export interface SchoolDistrict {
  id?: number
  name: string
  active: boolean
}

export interface CourseBuild {
  instructor_firstname: string
  instructor_lastname: string
  instructor_email: string
  school_district_name: string
  academic_year: string
  academic_year_short: string
  course_name: string
  course_shortname: string
  creator_email: string
  status: string
}

function convertApiUserToUser(apiUser: { email: string, is_admin: boolean, is_manager: boolean, id: number }): User {
  return {
    email: apiUser.email,
    isAdmin: apiUser.is_admin,
    isManager: apiUser.is_manager,
    id: apiUser.id
  }
}

export const ropeApi = {
  fetchUsers: async (): Promise<User[]> => {
    const response = await fetch('/api/user')
    if (!response.ok) {
      throw new Error('Failed to get users')
    }
    const usersFromApi = await response.json()
    const users: User[] = usersFromApi.map((user: { email: string, is_admin: boolean, is_manager: boolean, id: number }) =>
      convertApiUserToUser(user)
    )
    return users
  },

  addUser: async (email: string, isAdmin: boolean, isManager: boolean): Promise<User> => {
    const response = await fetch('/api/user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },

      body: JSON.stringify({ email, is_admin: isAdmin, is_manager: isManager })
    })
    if (!response.ok) {
      throw new Error('Failed to add user')
    }

    const newUserFromApi: { email: string, is_admin: boolean, is_manager: boolean, id: number } = await response.json()
    return convertApiUserToUser(newUserFromApi)
  },

  deleteUser: async (id: number): Promise<void> => {
    const response = await fetch(`/api/user/${id}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      throw new Error('Failed to delete user')
    }
  },

  updateUserPermissions: async (id: number, isAdmin: boolean, isManager: boolean, email: string): Promise<User> => {
    const response = await fetch(`/api/user/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ id, is_admin: isAdmin, is_manager: isManager, email })
    })

    if (!response.ok) {
      throw new Error('Failed to update user permissions')
    }

    const updatedUserFromApi: { id: number, email: string, is_admin: boolean, is_manager: boolean } = await response.json()
    return convertApiUserToUser(updatedUserFromApi)
  },
  getMoodleSettings: async (): Promise<MoodleSettings[]> => {
    const response = await fetch('/api/admin/settings/moodle')
    if (!response.ok) {
      throw new Error('Failed to get Moodle settings')
    }
    const settings: MoodleSettings[] = await response.json()
    return settings
  },
  createMoodleSetting: async (setting: MoodleSettings): Promise<MoodleSettings> => {
    const response = await fetch('/api/admin/settings/moodle', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(setting)
    })

    if (!response.ok) {
      throw new Error('Failed to create Moodle setting')
    }
    const newSetting: MoodleSettings = await response.json()
    return newSetting
  },
  updateMoodleSettings: async (id: number, settings: MoodleSettings): Promise<MoodleSettings> => {
    const response = await fetch(`/api/admin/settings/moodle/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(settings)
    })

    if (!response.ok) {
      throw new Error('Failed to update Moodle setting')
    }
    const updatedSetting: MoodleSettings = await response.json()
    return updatedSetting
  },
  getDistricts: async (): Promise<SchoolDistrict[]> => {
    const response = await fetch('/api/admin/settings/district')

    if (!response.ok) {
      throw new Error('Failed to get school districts')
    }
    const districts: SchoolDistrict[] = await response.json()
    return districts
  },

  createDistrict: async (district: SchoolDistrict): Promise<SchoolDistrict> => {
    const response = await fetch('/api/admin/settings/district', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(district)
    })

    if (!response.ok) {
      throw new Error('Failed to create school district')
    }
    const newDistrict: SchoolDistrict = await response.json()
    return newDistrict
  },

  updateDistrict: async (district: SchoolDistrict): Promise<SchoolDistrict> => {
    const response = await fetch(`/api/admin/settings/district/${district.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(district)
    })

    if (!response.ok) {
      throw new Error('Failed to update school district')
    }
    const updatedDistrict: SchoolDistrict = await response.json()
    return updatedDistrict
  },
  getCourseBuilds: async (academicYear?: string, instructorEmail?: string): Promise<CourseBuild[]> => {
    let url = '/api/moodle/course/build'
    const params = new URLSearchParams()

    if (academicYear != null) {
      params.append('academic_year', academicYear)
    }
    if (instructorEmail != null) {
      params.append('instructor_email', instructorEmail)
    }

    // Append params to the URL only if any exist
    if (Array.from(params).length > 0) {
      url += `?${params.toString()}`
    }
    console.log('url:', url)
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error('Failed to get course builds')
    }

    const courseBuilds: CourseBuild[] = await response.json()
    return courseBuilds
  },
  fakeGetCourseBuilds: async (academicYear?: string, instructorEmail?: string): Promise<CourseBuild[]> => {
    await new Promise(resolve => setTimeout(resolve, 100))

    const fakeCourseBuilds: CourseBuild[] = [
      {
        instructor_firstname: 'John',
        instructor_lastname: 'Doe',
        instructor_email: 'john.doe@example.com',
        school_district_name: 'Springfield School District',
        academic_year: '2024',
        academic_year_short: '23-24',
        course_name: 'Introduction to Chemistry',
        course_shortname: 'CHEM101',
        creator_email: 'admin@example.com',
        status: 'active'
      },
      {
        instructor_firstname: 'Jane',
        instructor_lastname: 'Smith',
        instructor_email: 'jane.smith@example.com',
        school_district_name: 'Riverside School District',
        academic_year: '2024',
        academic_year_short: '23-24',
        course_name: 'Advanced Mathematics',
        course_shortname: 'MATH301',
        creator_email: 'admin@example.com',
        status: 'active'
      },
      {
        instructor_firstname: 'Jane',
        instructor_lastname: 'Smith',
        instructor_email: 'jane.smith@example.com',
        school_district_name: 'Riverside School District',
        academic_year: '2024',
        academic_year_short: '23-24',
        course_name: 'Advanced Mathematics',
        course_shortname: 'MATH301',
        creator_email: 'admin@example.com',
        status: 'active'
      },
      {
        instructor_firstname: 'Jane',
        instructor_lastname: 'Smith',
        instructor_email: 'jane.smith@example.com',
        school_district_name: 'Riverside School District',
        academic_year: '2024',
        academic_year_short: '23-24',
        course_name: 'Advanced Mathematics',
        course_shortname: 'MATH301',
        creator_email: 'admin@example.com',
        status: 'active'
      },
      {
        instructor_firstname: 'Jane',
        instructor_lastname: 'Smith',
        instructor_email: 'jane.smith@example.com',
        school_district_name: 'Riverside School District',
        academic_year: '2024',
        academic_year_short: '23-24',
        course_name: 'Advanced Mathematics',
        course_shortname: 'MATH301',
        creator_email: 'admin@example.com',
        status: 'active'
      }
    ]
    return fakeCourseBuilds
  }

}
