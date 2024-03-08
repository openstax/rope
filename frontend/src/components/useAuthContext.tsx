import React, { useContext } from 'react'

// eslint-disable-next-line react-refresh/only-export-components
export enum AuthStatus {
  Unknown = 1,
  NotSignedIn,
  SignedIn
}

export interface AuthState {
  status: AuthStatus
  email: string | undefined
  isAdmin: boolean | undefined
  isManager: boolean | undefined
}

export const AuthContext = React.createContext<AuthState>({ status: AuthStatus.Unknown, isAdmin: false, isManager: false, email: undefined })

// eslint-disable-next-line react-refresh/only-export-components
export function useAuthContext(): AuthState {
  return useContext(AuthContext)
}
