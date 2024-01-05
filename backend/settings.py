import os

SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# Add / modify as desired for experimentation
MOCK_USERS = [
    {
        "email": "foobar@rice.edu",
        "is_admin": True,
        "is_manager": False,
    },
]
