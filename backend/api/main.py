from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from api.auth import verify_google_token
from api import settings
from api.utils import find_user_by_email

from pydantic import BaseModel


app = FastAPI(title="ROPE API", root_path="/api")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    https_only=True,
    session_cookie="ROPE.session",
    max_age=60 * 60,  # 1 hour
)


class GoogleLoginData(BaseModel):
    token: str


@app.post("/session")
def google_login(login_data: GoogleLoginData, request: Request):
    token = verify_google_token(login_data.token)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )
    # Need to actually look into the database for the email
    user = find_user_by_email(token["email"])
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized user",
        )

    # Create the session
