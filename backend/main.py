from fastapi import FastAPI, Request, HTTPException, Depends
from starlette.middleware.sessions import SessionMiddleware

from pydantic import BaseModel
from typing import Annotated

import uuid
from db import find_user_by_email
from auth import verify_google_token, verify_user, verify_admin, verify_manager
from sessions import create_session, destroy_session
import settings

app = FastAPI(root_path="/api")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    https_only=True,
    session_cookie="ROPE.session",
    max_age=60 * 60,  # 1 hour
)


class GoogleLoginData(BaseModel):
    token: str


@app.post("/login/google_auth")
def google_login(login_data: GoogleLoginData, request: Request):
    token = verify_google_token(login_data.token)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )
    user = find_user_by_email(token["email"])
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized user",
        )

    new_session_id = str(uuid.uuid4())
    create_session(new_session_id, user)
    request.session["session_id"] = new_session_id


@app.get("/user/current")
def get_current_user(current_user: Annotated[dict, Depends(verify_user)]):
    return current_user


@app.delete("/session", dependencies=[Depends(verify_user)])
def delete_session(request: Request):
    session_id = request.session.get("session_id")

    destroy_session(session_id)
    del request.session["session_id"]


@app.get("/admin_only", dependencies=[Depends(verify_admin)])
def admin_only():
    return


@app.get("/manager_only", dependencies=[Depends(verify_manager)])
def manager_only():
    return
