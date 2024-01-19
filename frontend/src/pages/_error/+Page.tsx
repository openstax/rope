import { usePageContext } from '../../renderer/usePageContext'

export function Page(): JSX.Element {
  const pageContext = usePageContext()
  let { abortReason } = pageContext
  if (abortReason === undefined) {
    abortReason = (pageContext.is404 === true) ? 'Page not found.' : 'Something went wrong.'
  }
  return (
    <Center>
      <p style={{ fontSize: '1.3em' }}>{abortReason}</p>
    </Center>
  )
}

function Center({ children }: { children: React.ReactNode }): JSX.Element {
  return (
    <div
      style={{
        height: 'calc(100vh - 100px)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}
    >
      {children}
    </div>
  )
}
