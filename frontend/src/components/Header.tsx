import styled from 'styled-components'
import { Link } from '../renderer/Link'
import { Logo } from './Logo'
import { AuthStatus, useAuthContext } from '../renderer/useAuthContext'

const HeaderContent = styled.div`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 8px;
  color: #fff;
  background-color: #005047;

  & > *:last-child {
    margin-left: auto;
  }

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
    background-color:rgba(255, 255, 255, 0.2);
  }
  & > *:hover {
    background-color: rgba(255, 255, 255, 0.2); 
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
        <Link className="navitem" href="/about">
          About
        </Link>
        {authContext.status === AuthStatus.SignedIn
          ? <a href="#" onClick={logout}>Logout</a>
          : <a href="/login" >Login</a> }
        {children}
      </HeaderContent>
    </>
  )
}
