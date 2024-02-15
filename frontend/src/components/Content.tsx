import styled from 'styled-components'

const StyledContent = styled.div`
    margin: 10px;
`

export function Content({ children }: { children: React.ReactNode }): JSX.Element {
  return (
    <StyledContent
    >
      {children}
    </StyledContent>
  )
}
