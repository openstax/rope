// https://vike.dev/onRenderClient

import ReactDOM from 'react-dom/client'
import { PageShell } from './PageShell'
import { getPageTitle } from './getPageTitle'
import type { OnRenderClientAsync } from 'vike/types'

let root: ReactDOM.Root
export const onRenderClient: OnRenderClientAsync = async (pageContext): ReturnType<OnRenderClientAsync> => {
  const { Page } = pageContext

  // This onRenderClient() hook only supports SSR, see https://vike.dev/render-modes for how to modify onRenderClient()
  // to support SPA
  // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
  if (!Page) throw new Error('My onRenderClient() hook expects pageContext.Page to be defined')

  const container = document.getElementById('react-root')
  if (container === null) throw new Error('DOM element #react-root not found')

  const page = (
    <PageShell pageContext={pageContext}>
      <Page />
    </PageShell>
  )
  if (pageContext.isHydration) {
    root = ReactDOM.hydrateRoot(container, page)
  } else {
    // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
    if (!root) {
      root = ReactDOM.createRoot(container)
    }
    root.render(page)
  }
  document.title = getPageTitle(pageContext)
}
