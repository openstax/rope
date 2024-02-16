import { useAuthContext } from '../../components/useAuthContext'
import { useState, useEffect } from 'react'
import styled from 'styled-components'

interface User {
  email: string
  is_admin: boolean
  is_manager: boolean
  id: number
}

const Container = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  margin-top: 50px;
`

const Table = styled.table`
  width: 80%;
  margin-bottom: 20px;
`

const Th = styled.th`
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ccc;
`

const Td = styled.td`
  padding: 10px;
  border-bottom: 1px solid #ccc;
`

const Input = styled.input`
  margin-bottom: 10px;
  padding: 5px;
`

const Button = styled.button`
  padding: 8px 16px;
  margin-top: 10px;
`

const ErrorTag = styled.p`
  color: red
`

function Page(): JSX.Element {
  const authContext = useAuthContext()

  const [users, setUsers] = useState<User[]>([])
  const [newUser, setNewUser] = useState<{ email: string, isAdmin: boolean, isManager: boolean }>({ email: '', isAdmin: false, isManager: false })
  const [error, setError] = useState<string>('')

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target
    setNewUser({ ...newUser, [name]: value })
  }

  useEffect(() => {
    if (authContext.isAdmin) {
      fetchUsers().catch((error) => {
        console.error('Fetch error', error)
      })
    }
  }, [authContext.isAdmin])

  const fetchUsers = async (): Promise<void> => {
    const response = await fetch('/api/user')
    if (!response.ok) {
      throw new Error('Failed to get users')
    }
    const data: User[] = await response.json()
    console.log(data)
    setUsers(data)
  }

  const addUser = async (): Promise<void> => {
    const { email, isAdmin, isManager } = newUser

    if (email.match(/^\S+@rice\.edu$/) == null) {
      setError('Please enter a valid Rice University email')
      return
    }
    try {
      const response = await fetch('/api/user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, is_admin: isAdmin, is_manager: isManager })
      })

      if (!response.ok) {
        setError('Failed to add user')
        throw new Error('Failed to add user')
      }

      const data: User = await response.json()
      setUsers([...users, data])
      setNewUser({ email: '', isAdmin: false, isManager: false })
      setError('')
    } catch (error) {
      console.error('Add user error', error)
    }
  }

  const deleteUser = async (id: number): Promise<void> => {
    try {
      const response = await fetch(`/api/user/${id}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        setError('Failed to delete user')
        throw new Error('Failed to delete user')
      }

      setUsers(users.filter(user => user.id !== id))
    } catch (error) {
      console.error('Delete user error', error)
    }
  }

  const updateUserPermissions = async (id: number, isAdmin: boolean, isManager: boolean, email: string): Promise<void> => {
    try {
      const response = await fetch(`/api/user/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id, is_admin: isAdmin, is_manager: isManager, email })
      })

      if (!response.ok) {
        setError('Failed to update user permissions')
        throw new Error('Failed to update user permissions')
      }

      setUsers(users.map(user => {
        if (user.id === id) {
          return { ...user, is_admin: isAdmin, is_manager: isManager, email }
        }
        return user
      }))
    } catch (error) {
      console.error('Update user permissions error', error)
    }
  }

  const renderUsers = users.length > 0
    ? (
        users.map(user => (
        <tr key={user.email}>
          <Td>{user.email}</Td>
          <Td>
            <input
              type="checkbox"
              name="isAdmin"
              checked={user.is_admin}
              onChange={(e) => {
                const isChecked = e.target.checked
                void updateUserPermissions(user.id, isChecked, user.is_manager, user.email)
              }}
            />
          </Td>
          <Td>
            <input
              type="checkbox"
              name="isManager"
              checked={user.is_manager}
              onChange={(e) => {
                const isChecked = e.target.checked
                void updateUserPermissions(user.id, user.is_admin, isChecked, user.email)
              }}
            />
          </Td>
          <Td><Button onClick={() => { void deleteUser(user.id) }}>Remove user</Button></Td>
        </tr>
        ))
      )
    : (
      <tr>
        <Td colSpan={4}>No users found</Td>
      </tr>
      )

  return (
    <Container>
      {authContext.isAdmin
        ? <>
          <h2>User Management</h2>
          {(error !== '') && <ErrorTag>{error}</ErrorTag>}
          <Table>
            <thead>
              <tr>
                <Th>Email</Th>
                <Th>Admin</Th>
                <Th>Manager</Th>
                <Th></Th>
              </tr>
            </thead>
            <tbody>
              {renderUsers}
            </tbody>
          </Table>
          <h3>Create User</h3>
          <div>
            <Input type="email" placeholder='New user email' name="email" value={newUser.email.trim()} onChange={handleInputChange} />
          </div>
          <div>
            <label>
              Admin
              <Input type="checkbox" name="isAdmin" checked={newUser.isAdmin} onChange={() => { setNewUser({ ...newUser, isAdmin: !newUser.isAdmin }) }} />
            </label>
          </div>
          <div>
            <label>
              Manager
              <Input type="checkbox" name="isManager" checked={newUser.isManager} onChange={() => { setNewUser({ ...newUser, isManager: !newUser.isManager }) }} />
            </label>
          </div>
          <Button onClick={() => { void addUser() }}>Add User</Button>
        </>
        : <p>This page is admin only</p>}
    </Container>
  )
}

export { Page }
