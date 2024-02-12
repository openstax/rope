from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import UniqueConstraint

from datetime import datetime, timezone


def generate_utc_timestamp():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        default=generate_utc_timestamp,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=generate_utc_timestamp,
        onupdate=generate_utc_timestamp,
    )


class UserAccount(Base):
    __tablename__ = 'user_account'
    __table_args__ = (
        UniqueConstraint('email'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str]
    is_manager: Mapped[bool]
    is_admin: Mapped[bool]


class SchoolDistrict(Base):
    __tablename__ = 'school_district'
    __table_args__ = (
        UniqueConstraint('name'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    active: Mapped[bool]
