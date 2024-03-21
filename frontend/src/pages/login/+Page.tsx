import { GoogleOAuthProvider, GoogleLogin, type CredentialResponse } from '@react-oauth/google'
import { ENV } from '../../lib/env'
import styled from 'styled-components'
import { useState } from 'react'
import { ropeApi } from '../../utils/ropeApi'
const CenteredContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 80vh;
`

const ErrorMessage = styled.p`
  color: red;
  margin-top: 10px; /* Adjust as needed */
`

function Page(): JSX.Element {
  const [error, setError] = useState<string>('')

  const handleLogin = (credentialResponse: CredentialResponse): void => {
    const token = credentialResponse.credential
    if (token !== undefined) {
      ropeApi.login(token)
        .then(() => {
          window.location.href = '/'
        })
        .catch(error => {
          console.error('Error establishing session:', error)
          setError('Login failed')
        })
    } else {
      console.error('Credential is undefined')
      setError('Login failed')
    }
  }

  return (
    <>
    <CenteredContainer>
      <GoogleOAuthProvider clientId={ENV.GOOGLE_CLIENT_ID}>
        <GoogleLogin
          onSuccess={handleLogin}
          onError={() => {
            console.error('Google login Failed')
          }}
          hosted_domain='rice.edu'
        />
      </GoogleOAuthProvider>
      {error !== '' ? <ErrorMessage>{error}</ErrorMessage> : <></>}
      </CenteredContainer>

    </>
  )
}

export { Page }
