export interface User {
  email: string
  isAdmin: boolean
  isManager: boolean
  id: number
}

export const ropeApi = {
  fetchUsers: async (): Promise<User[]> => {
    const response = await fetch('/api/user')
    if (!response.ok) {
      throw new Error('Failed to get users')
    }
    const usersFromApi = await response.json()
    const users: User[] = usersFromApi.map((user: { is_admin: boolean, is_manager: boolean }) => ({
      ...user,
      isAdmin: user.is_admin,
      isManager: user.is_manager
    }))
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

    return await response.json()
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

    return await response.json()
  }
}
