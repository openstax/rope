from fastapi import Request, HTTPException, Depends
from google.oauth2 import id_token
from google.auth.transport import requests
from typing import Annotated

from sessions import get_session
import settings


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


def verify_user(request: Request):
    session_id = request.session.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Unauthenticated",
        )

    maybe_user = get_session(session_id)

    if not maybe_user:
        raise HTTPException(
            status_code=401,
            detail="Unauthenticated",
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
