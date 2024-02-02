from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

import uuid
from pydantic import BaseModel
from typing import Annotated

from rope.api.auth import verify_google_token, verify_user, verify_admin
from rope.api import settings
from rope.api.database import SessionLocal, get_user_by_email, get_all_users
from rope.api.sessions import create_session, destroy_session, get_request_session


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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/session")
def google_login(
    login_data: GoogleLoginData,
    session=Depends(get_request_session),
    db: Session = Depends(get_db),
):
    token = verify_google_token(login_data.token)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )
    user = get_user_by_email(db, token["email"])
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized user",
        )
    user_data = {
        "email": user.email,
        "is_manager": user.is_manager,
        "is_admin": user.is_admin,
    }

    new_session_id = str(uuid.uuid4())
    create_session(new_session_id, user_data)
    session["session_id"] = new_session_id


@app.get("/user/current")
def get_current_user(current_user: Annotated[dict, Depends(verify_user)]):
    return current_user


@app.delete("/session", dependencies=[Depends(verify_user)])
def delete_session(session=Depends(get_request_session)):
    session_id = session.get("session_id")
    destroy_session(session_id)
    del session["session_id"]


@app.get("/user", dependencies=[Depends(verify_admin)])
def get_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    return users
