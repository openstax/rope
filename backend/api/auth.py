from google.oauth2 import id_token
from google.auth.transport import requests

from api import settings


def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        # Do we need to check for domain?
        return idinfo

    except ValueError:
        return None
