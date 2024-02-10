import styled from 'styled-components'

const StyledLayout = styled.div`
`

export function Layout({ children }: { children: React.ReactNode }): JSX.Element {
  return (
    <StyledLayout>
      {children}
    </StyledLayout>
  )
}
