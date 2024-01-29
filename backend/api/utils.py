from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.schema import UserAccount

import os

pg_server = os.getenv("POSTGRES_SERVER", "")
pg_db = os.getenv("POSTGRES_DB", "")
pg_user = os.getenv("POSTGRES_USER", "")
pg_password = os.getenv("POSTGRES_PASSWORD", "")
sqlalchemy_url = f"postgresql://{pg_user}:{pg_password}@{pg_server}/{pg_db}"

engine = create_engine(sqlalchemy_url)
session_factory = sessionmaker(engine)


def find_user_by_email(email):
    with session_factory() as session:
        user = session.query(UserAccount).filter_by(email=email).one()
        # If it returns the user object or nothing, then I think this is fine.
        # Otherwise, might need to do if user["email"] == email.
        if user:
            return user

        return None
