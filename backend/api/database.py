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
        return None
    if len(user) > 1:
        raise MultipleResultsFound  # pragma: no cover
    return user[0]


def get_all_users(db: Session):
    users = db.query(UserAccount).all()
    return users


def create_db_user(db: Session, user):
    new_user = UserAccount(
        email=user.email, is_manager=user.is_manager, is_admin=user.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_db_user(db: Session, user):
    user_db = db.query(UserAccount).filter(UserAccount.id == user.id).first()
    if not user_db:
        raise NoResultFound
    user_db.email = user.email
    user_db.is_manager = user.is_manager
    user_db.is_admin = user.is_admin
    db.commit()
    db.refresh(user_db)
    return user_db


def delete_db_user(db: Session, id: int):
    rows_deleted = db.query(UserAccount).filter(UserAccount.id == id).delete()
    db.commit()
    return rows_deleted
