import React, { useEffect, useState } from 'react'
import { PageContextProvider } from '../components/usePageContext'
import type { PageContext } from 'vike/types'
import './PageShell.css'
import { Header } from '../components/Header'
import { AuthGuard } from '../components/AuthGuard'
import { Content } from '../components/Content'
import { AuthContext, AuthStatus, type AuthState } from '../components/useAuthContext'
import { ropeApi } from '../utils/ropeApi'

export function PageShell({ children, pageContext }: { children: React.ReactNode, pageContext: PageContext }): JSX.Element {
  const [authState, setAuthState] = useState<AuthState>({ status: AuthStatus.Unknown, email: undefined, isAdmin: false, isManager: false })

  useEffect(() => {
    const fetchCurrentUser = async (): Promise<void> => {
      const user = await ropeApi.getCurrentUser()

      if (user != null) {
        setAuthState({
          status: AuthStatus.SignedIn,
          email: user.email,
          isAdmin: user.isAdmin,
          isManager: user.isManager
        })
      } else {
        setAuthState({
          status: AuthStatus.NotSignedIn,
          email: undefined,
          isAdmin: false,
          isManager: false
        })
      }
    }

    fetchCurrentUser().catch(console.error)
  }, [])

  const logout = async (): Promise<void> => {
    const success = await ropeApi.logoutUser()
    if (success) {
      setAuthState({
        status: AuthStatus.NotSignedIn,
        email: undefined,
        isAdmin: false,
        isManager: false
      })
    }
  }

  return (
    <React.StrictMode>
      <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={authState}>
          <AuthGuard>
              <Header logout={() => { void logout() }}>
              </Header>
              <Content>{children}</Content>
          </AuthGuard>
        </AuthContext.Provider>
      </PageContextProvider>
    </React.StrictMode>
  )
}
