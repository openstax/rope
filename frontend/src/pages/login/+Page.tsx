import { GoogleOAuthProvider, GoogleLogin, type CredentialResponse } from '@react-oauth/google'
import { ENV } from '../../lib/env'
import styled from 'styled-components'

const CenteredContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
`

function Page(): JSX.Element {
  const login = async (token: string): Promise<void> => {
    const resp = await fetch(
      '/api/session',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          token
        })
      }
    )

    if (resp.status !== 200) {
      throw new Error('Error: Login failed')
    }
  }
  const handleLogin = (credentialResponse: CredentialResponse): void => {
    const token = credentialResponse.credential
    if (token !== undefined) {
      login(token)
        .then(() => {
          window.location.href = '/'
        })
        .catch(error => {
          console.error('Error establishing session:', error)
        })
    } else {
      console.error('Credential is undefined')
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
      </CenteredContainer>
    </>
  )
}

export { Page }
