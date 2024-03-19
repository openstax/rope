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
  },
  logoutUser: async (): Promise<boolean> => {
    try {
      const response = await fetch('/api/session', { method: 'DELETE' })
      return response.ok
    } catch (error) {
      console.error('Logout error:', error)
      return false
    }
  }

}
