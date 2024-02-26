from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException, Depends
from typing import Annotated

from rope.api import settings
from rope.api.sessions import get_request_session, get_session


def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        if idinfo["hd"] != "rice.edu":
            return None

        return idinfo

    except ValueError:
        return None


def verify_user(session=Depends(get_request_session)):
    session_id = session.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Unauthenticated user",
        )

    maybe_user = get_session(session_id)

    if not maybe_user:
        raise HTTPException(
            status_code=401,
            detail="Unauthenticated user",
        )

    return maybe_user


def verify_admin(current_user: Annotated[dict, Depends(verify_user)]):
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized to perform this request",
        )

    return current_user


def verify_manager(current_user: Annotated[dict, Depends(verify_user)]):
    if not current_user["is_admin"] and not current_user["is_manager"]:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized to perform this request",
        )
    return current_user
