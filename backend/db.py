from settings import MOCK_USERS


def find_user_by_email(email):
    for user in MOCK_USERS:
        if user["email"] == email:
            return user
    return None
