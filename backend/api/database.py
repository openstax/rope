from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from rope.db.schema import UserAccount
from rope.api.settings import PG_USER, PG_PASSWORD, PG_SERVER, PG_DB

SQLALCHEMY_DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_SERVER}/{PG_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_user_by_email(db: Session, email: str):
    user = db.query(UserAccount).filter(UserAccount.email == email).all()
    if not user:
        raise NoResultFound
    if len(user) > 1:
        raise MultipleResultsFound
    return user[0]
