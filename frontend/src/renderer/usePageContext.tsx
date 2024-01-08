// `usePageContext` allows us to access `pageContext` in any React component.
// See https://vike.dev/pageContext-anywhere

import React, { useContext } from 'react'
import type { PageContext } from 'vike/types'

const Context = React.createContext<PageContext>(undefined as unknown as PageContext)

export function PageContextProvider({ pageContext, children }: { pageContext: PageContext, children: React.ReactNode }): JSX.Element {
  return <Context.Provider value={pageContext}>{children}</Context.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function usePageContext(): PageContext {
  const pageContext = useContext(Context)
  return pageContext
}
