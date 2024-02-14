// https://vike.dev/onRenderHtml

import ReactDOMServer from 'react-dom/server'
import { PageShell } from './PageShell'
import { escapeInject, dangerouslySkipEscape } from 'vike/server'
import type { OnRenderHtmlAsync } from 'vike/types'
import { getPageTitle } from './getPageTitle'
import { ServerStyleSheet } from 'styled-components'

export const onRenderHtml: OnRenderHtmlAsync = async (pageContext): ReturnType<OnRenderHtmlAsync> => {
  const { Page } = pageContext

  // This onRenderHtml() hook only supports SSR, see https://vike.dev/render-modes for how to modify
  // onRenderHtml() to support SPA
  // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
  if (!Page) throw new Error('My onRenderHtml() hook expects pageContext.Page to be defined')

  // Alternativly, we can use an HTML stream, see https://vike.dev/stream
  const sheet = new ServerStyleSheet()

  const pageHtml = ReactDOMServer.renderToString(
    sheet.collectStyles(
    <PageShell pageContext={pageContext}>
      <Page />
    </PageShell>
    )
  )

  // See https://vike.dev/head
  const title = getPageTitle(pageContext)
  const desc = pageContext.data?.description ?? pageContext.config.description ?? 'ROPE'

  const documentHtml = escapeInject`<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="description" content="${desc}" />
        <title>${title}</title>
        <style>${dangerouslySkipEscape(sheet.getStyleTags())}</style>
      </head>
      <body>
        <div id="react-root">${dangerouslySkipEscape(pageHtml)}</div>
      </body>
    </html>`

  return {
    documentHtml,
    pageContext: {
      // We can add custom pageContext properties here, see https://vike.dev/pageContext#custom
    }
  }
}
