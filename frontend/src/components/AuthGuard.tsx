import { useEffect } from 'react'
import { AuthStatus, useAuthContext } from '../renderer/useAuthContext'
import { usePageContext } from '../renderer/usePageContext'

export function AuthGuard({ children }: { children: React.ReactNode }): JSX.Element {
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
    return <>{children}</>
  }

  return <></>
}
