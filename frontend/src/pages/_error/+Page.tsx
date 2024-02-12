import styled from 'styled-components'
import { usePageContext } from '../../renderer/usePageContext'

const Center = styled.div`
  height: calc(100vh - 100px);
  display: flex;
  justify-content: center;
  align-items: center;
`

const Paragraph = styled.p`
  font-size: 1.3em;
`

export function Page(): JSX.Element {
  const pageContext = usePageContext()
  let { abortReason } = pageContext
  if (abortReason === undefined) {
    abortReason = pageContext.is404 === true ? 'Page not found.' : 'Something went wrong.'
  }
  return (
    <Center>
      <Paragraph>{abortReason}</Paragraph>
    </Center>
  )
}
