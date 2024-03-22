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

export type MoodleUser = {
  firstName: string
  lastName: string
  email: string
} | null

export interface CourseBuild {
  instructorFirstName: string
  instructorLastName: string
  instructorEmail: string
  schoolDistrictName: string
  academicYear: string
  academicYearShort: string
  courseName: string
  courseShortName: string
  creatorEmail: string
  status: string
  courseId?: string
  courseEnrollmentUrl?: string
  courseEnrollmentKey?: string
}

function convertApiUserToUser(apiUser: { email: string, is_admin: boolean, is_manager: boolean, id: number }): User {
  return {
    email: apiUser.email,
    isAdmin: apiUser.is_admin,
    isManager: apiUser.is_manager,
    id: apiUser.id
  }
}

function convertApiCourseBuildToCourseBuild(apiCourseBuild: {
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
  course_id?: string
  course_enrollment_url?: string
  course_enrollment_key?: string

}): CourseBuild {
  return {
    instructorFirstName: apiCourseBuild.instructor_firstname,
    instructorLastName: apiCourseBuild.instructor_lastname,
    instructorEmail: apiCourseBuild.instructor_email,
    schoolDistrictName: apiCourseBuild.school_district_name,
    academicYear: apiCourseBuild.academic_year,
    academicYearShort: apiCourseBuild.academic_year_short,
    courseName: apiCourseBuild.course_name,
    courseShortName: apiCourseBuild.course_shortname,
    creatorEmail: apiCourseBuild.creator_email,
    status: apiCourseBuild.status,
    courseId: apiCourseBuild.course_id,
    courseEnrollmentUrl: apiCourseBuild.course_enrollment_url,
    courseEnrollmentKey: apiCourseBuild.course_enrollment_key
  }
}

function convertApiMoodleUsertoMoodleUser(apiMoodleUser: { first_name: string, last_name: string, email: string }): MoodleUser | null {
  if (apiMoodleUser === null) {
    return null
  }
  return {
    firstName: apiMoodleUser.first_name,
    lastName: apiMoodleUser.last_name,
    email: apiMoodleUser.email
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

  getMoodleUser: async (email: string): Promise<MoodleUser> => {
    const response = await fetch(`/api/moodle/user?email=${email}`)
    if (!response.ok) {
      throw new Error('Failed to get the user')
    }

    const newMoodleUserFromApi: { first_name: string, last_name: string, email: string } = await response.json()
    return convertApiMoodleUsertoMoodleUser(newMoodleUserFromApi)
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

  getCourseBuilds: async (academicYear: string, instructorEmail: string): Promise<CourseBuild[]> => {
    const response = await fetch(`/api/moodle/course/build?academic_year=${academicYear}&instructor_email=${instructorEmail}`)

    if (!response.ok) {
      throw new Error('Failed to get course builds')
    }

    const courseBuildsFromApi = await response.json()
    const courseBuilds: CourseBuild[] = courseBuildsFromApi.map((courseBuild: {
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
    }) => convertApiCourseBuildToCourseBuild(courseBuild))
    return courseBuilds
  },
  getAllCourseBuilds: async (): Promise<CourseBuild[]> => {
    const response = await fetch('/api/moodle/course/build')

    if (!response.ok) {
      throw new Error('Failed to get all course builds')
    }

    const courseBuildsFromApi = await response.json()
    const courseBuilds: CourseBuild[] = courseBuildsFromApi.map((courseBuild: {
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
      course_id: string
      course_enrollment_url: string
      course_enrollment_key: string
    }) => convertApiCourseBuildToCourseBuild(courseBuild))
    return courseBuilds
  },

  createCourseBuild: async (instructorFirstName: string, instructorLastName: string, instructorEmail: string, schoolDistrictName: string): Promise<CourseBuild> => {
    const courseSettings = {
      instructor_firstname: instructorFirstName,
      instructor_lastname: instructorLastName,
      instructor_email: instructorEmail,
      school_district_name: schoolDistrictName
    }
    const response = await fetch('/api/moodle/course/build', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(courseSettings)
    })

    if (!response.ok) {
      throw new Error('Failed to create course build setting')
    }

    const newCourseBuildFromApi: {
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
    } = await response.json()
    return convertApiCourseBuildToCourseBuild(newCourseBuildFromApi)
  },
  getCurrentUser: async (): Promise<{ email: string, isAdmin: boolean, isManager: boolean } | null> => {
    const response = await fetch('/api/user/current')
    if (!response.ok) {
      console.error('Failed to fetch current user')
      return null
    }
    const data = await response.json()
    return {
      email: data.email,
      isAdmin: data.is_admin,
      isManager: data.is_manager
    }
  },
  logoutUser: async (): Promise<boolean> => {
    try {
      const response = await fetch('/api/session', { method: 'DELETE' })
      return response.ok
    } catch (error) {
      console.error('Logout error:', error)
      return false
    }
  },
  login: async (token: string): Promise<void> => {
    const response = await fetch('/api/session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        token
      })
    })
    if (!response.ok) {
      throw new Error('Login failed')
    }
  }
}
