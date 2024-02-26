from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import uuid

from rope.api.auth import verify_google_token, verify_user
from rope.api import database
from rope.api.sessions import (
    create_session,
    destroy_session,
    get_request_session,
    get_session,
)
from rope.api.models import GoogleLoginData

router = APIRouter(
    prefix="/session",
    tags=["session"],
)


@router.post("/")
def google_login(
    login_data: GoogleLoginData,
    session=Depends(get_request_session),
    db: Session = Depends(database.get_db),
):
    token = verify_google_token(login_data.token)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )
    user = database.get_user_by_email(db, token["email"])
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
    user_session_data = get_session(session["session_id"])
    return user_session_data


@router.delete("/", dependencies=[Depends(verify_user)])
def delete_session(session=Depends(get_request_session)):
    session_id = session.get("session_id")
    destroy_session(session_id)
    del session["session_id"]
