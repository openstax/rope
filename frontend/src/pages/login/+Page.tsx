import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google'
import { ENV } from '../../lib/env'

export { Page }

function Page() {
  const login = async (token: string): Promise<void> => {
    const resp = await fetch(
      '/api/login/google_auth',
      {
        method: 'POST',
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          token: token
        })
      }
    )

    if (resp.status !== 200) {
      throw new Error("Error establishing session")
    }
  }

  return (
    <>
      <h1>Login</h1>
      <GoogleOAuthProvider clientId={ENV.GOOGLE_CLIENT_ID}>
        <GoogleLogin
          onSuccess={credentialResponse => {
            login(credentialResponse.credential!).then(() => {
              window.location.href='/'
            })
          }}
          onError={() => {
            console.error('Google login Failed')
          }}
          hosted_domain='rice.edu'
        />
      </GoogleOAuthProvider>
    </>
  )
}