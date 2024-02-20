import styled from 'styled-components'
import { Link } from './Link'
import { Logo } from './Logo'
import { AuthStatus, useAuthContext } from './useAuthContext'

const HeaderContent = styled.div`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 8px;
  color: #fff;
  background-color: #005047;

  & > * {
    margin-right: 8px;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background-color: transparent;
    color: #fff;
    cursor: pointer;
    text-decoration: none;
    transition: background-color 0.3s ease;
  }

  .navitem.is-active {
    background-color: rgba(255, 255, 255, 0.2);
  }

  & > *:hover {
    background-color: rgba(255, 255, 255, 0.2); 
  }

  .right-element {
    margin-left: auto;
  }
`

interface HeaderProps {
  children?: React.ReactNode
  logout: () => void
}

export function Header({ children, logout }: HeaderProps): JSX.Element {
  const authContext = useAuthContext()

  return (
    <>
      <HeaderContent>
        <Logo />
        <Link className="navitem" href="/">
          Home
        </Link>
        <Link className="navitem" href="/courses">
          Courses
        </Link>
        {authContext.isAdmin
          ? <Link className="navitem" href="/users">
          Users
        </Link>
          : <></>}
        {authContext.status === AuthStatus.SignedIn
          ? <a className="right-element" href="#" onClick={logout}>Logout</a>
          : <></>}
        {children}
      </HeaderContent>
    </>
  )
}
