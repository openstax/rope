export interface User {
  email: string
  isAdmin: boolean
  isManager: boolean
  id: number
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
      console.log(response)
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
  getCurrentUser: async (): Promise<{ email?: string, isAdmin?: boolean, isManager?: boolean } | null> => {
    try {
      const response = await fetch('/api/user/current')
      if (!response.ok) {
        throw new Error('Failed to fetch current user')
      }
      const data = await response.json()
      return {
        email: data.email,
        isAdmin: data.is_admin,
        isManager: data.is_manager
      }
    } catch (error) {
      console.error(error)
      return null
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
