from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone


def generate_utc_timestamp():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        default=generate_utc_timestamp
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=generate_utc_timestamp,
        onupdate=generate_utc_timestamp
    )


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str]
    is_manager: Mapped[bool]
    is_admin: Mapped[bool]
