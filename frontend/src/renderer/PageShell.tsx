import React, { useEffect, useState } from 'react'
import logo from './logo.svg'
import { PageContextProvider, usePageContext } from './usePageContext'
import type { PageContext } from 'vike/types'
import './PageShell.css'
import { Link } from './Link'
import { AuthContext, AuthStatus, useAuthContext, AuthState } from './useAuthContext'

export { PageShell }

function PageShell({ children, pageContext }: { children: React.ReactNode; pageContext: PageContext }) {
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

    getCurrentUser()
  }, [])

  const logout = async (): Promise<void> => {
    const resp = await fetch('/api/session', { method: 'DELETE' })
    if (resp.status === 200) {
      setAuthState({
        status: AuthStatus.NotSignedIn,
        email: undefined,
        isAdmin: false,
        isManager: false
      })
    }
  }


  const admin_only = async (): Promise<void> => {
    await fetch('/api/admin_only')
  }

  const manager_only = async (): Promise<void> => {
    await fetch('/api/manager_only')
  }

  return (
    <React.StrictMode>
      <PageContextProvider pageContext={pageContext}>
        <AuthContext.Provider value={authState}>
          <AuthGuard>
            <Layout>
              <Sidebar>
                <Logo />
                <Link className="navitem" href="/">
                  Home
                </Link>
                <Link className="navitem" href="/about">
                  About
                </Link>
                <a href="#" onClick={admin_only}>Test Admin request</a>
                <a href="#" onClick={manager_only}>Test Manager request</a>
                <a href="#" onClick={logout}>Logout</a>
              </Sidebar>
              <Content>{children}</Content>
            </Layout>
          </AuthGuard>
        </AuthContext.Provider>
      </PageContextProvider>
    </React.StrictMode>
  )
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        display: 'flex',
        maxWidth: 900,
        margin: 'auto'
      }}
    >
      {children}
    </div>
  )
}

function Sidebar({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        padding: 20,
        flexShrink: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        lineHeight: '1.8em'
      }}
    >
      {children}
    </div>
  )
}

function Content({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        padding: 20,
        paddingBottom: 50,
        borderLeft: '2px solid #eee',
        minHeight: '100vh'
      }}
    >
      {children}
    </div>
  )
}

function Logo() {
  return (
    <div
      style={{
        marginTop: 20,
        marginBottom: 10
      }}
    >
      <a href="/">
        <img src={logo} height={64} width={64} alt="logo" />
      </a>
    </div>
  )
}

function AuthGuard({ children }: { children: React.ReactNode }) {
  const authContext = useAuthContext()
  const pageContext = usePageContext()

  useEffect(() => {
    if ((authContext.status === AuthStatus.NotSignedIn) && (pageContext.urlPathname !== '/login')) {
      window.location.href = '/login'
    }

    if ((authContext.status === AuthStatus.SignedIn) && (pageContext.urlPathname === '/login')) {
      window.location.href = '/'
    }

  }, [authContext, pageContext])

  if ((authContext.status === AuthStatus.SignedIn) || (pageContext.urlPathname === '/login')) {
    return children
  }

  return <></>
}
