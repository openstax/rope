import logo from '../assets/logo.svg'

export function Logo(): JSX.Element {
  return (
    <div
    >
      <a href="/">
        <img src={logo} height={64} width={64} alt="logo" />
      </a>
    </div>
  )
}
