import React, { useEffect, useState } from 'react'
import { PageContextProvider } from '../components/usePageContext'
import type { PageContext } from 'vike/types'
import './PageShell.css'
import { Header } from '../components/Header'
import { AuthGuard } from '../components/AuthGuard'
import { Content } from '../components/Content'
import { AuthContext, AuthStatus, type AuthState } from '../components/useAuthContext'

export function PageShell({ children, pageContext }: { children: React.ReactNode, pageContext: PageContext }): JSX.Element {
  const [authState, setAuthState] = useState<AuthState>({ status: AuthStatus.Unknown, email: undefined, isAdmin: false, isManager: false })

  useEffect(() => {
    const getCurrentUser = async (): Promise<void> => {
      const resp = await fetch('/api/user/current')
      if (resp.status !== 200) {
        setAuthState({
          status: AuthStatus.NotSignedIn,
          email: undefined,
          isAdmin: false,
          isManager: false
        })
        return
      }
      const data = await resp.json()
      setAuthState({
        status: AuthStatus.SignedIn,
        email: data.email,
        isAdmin: data.is_admin,
        isManager: data.is_manager
      })
    }

    getCurrentUser().catch((err) => {
      console.error(err)
    })
  }, [])

  const logout = (): void => {
    fetch('/api/session', { method: 'DELETE' })
      .then(resp => {
        if (resp.status === 200) {
          setAuthState({
            status: AuthStatus.NotSignedIn,
            email: undefined,
            isAdmin: false,
            isManager: false
          })
        }
      })
      .catch(error => {
        console.error('Logout error:', error)
      })
  }

  return (
    <React.StrictMode>
      <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={authState}>
          <AuthGuard>
              <Header logout={logout}>
              </Header>
              <Content>{children}</Content>
          </AuthGuard>
        </AuthContext.Provider>
      </PageContextProvider>
    </React.StrictMode>
  )
}
