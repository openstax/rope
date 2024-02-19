from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import UniqueConstraint, ForeignKey

from datetime import datetime, timezone

from typing import Optional
import enum


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
    __tablename__ = "user_account"
    __table_args__ = (
        UniqueConstraint("email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str]
    is_manager: Mapped[bool]
    is_admin: Mapped[bool]


class SchoolDistrict(Base):
    __tablename__ = "school_district"
    __table_args__ = (
        UniqueConstraint("name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    active: Mapped[bool]


class MoodleSetting(Base):
    __tablename__ = "moodle_setting"
    __table_args__ = (
        UniqueConstraint("name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    value: Mapped[str]


class CourseStatus(enum.Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CourseBuild(Base):
    __tablename__ = "course_build"
    __table_args__ = (
        UniqueConstraint("course_shortname"),
        UniqueConstraint("instructor_email", "academic_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instructor_firstname: Mapped[str]
    instructor_lastname: Mapped[str]
    instructor_email: Mapped[str]
    course_name: Mapped[str]
    course_shortname: Mapped[str]
    course_category: Mapped[int]
    course_id: Mapped[Optional[int]]
    course_enrollment_url: Mapped[Optional[str]]
    course_enrollment_key: Mapped[Optional[str]]
    school_district: Mapped[int] = mapped_column(ForeignKey("school_district.id"))
    academic_year: Mapped[str]
    academic_year_short: Mapped[str]
    base_course_id: Mapped[int]
    status: Mapped[CourseStatus]
    creator: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
