from typing import Optional
import enum

from pydantic import BaseModel


class GoogleLoginData(BaseModel):
    token: str


class BaseUser(BaseModel):
    email: str
    is_manager: bool
    is_admin: bool


class FullUser(BaseUser):
    id: int


class BaseSchoolDistrict(BaseModel):
    name: str
    active: bool


class FullSchoolDistrict(BaseSchoolDistrict):
    id: int


class BaseMoodleSettings(BaseModel):
    name: str
    value: str


class FullMoodleSettings(BaseMoodleSettings):
    id: int


class BaseCourseBuildSettings(BaseModel):
    instructor_firstname: str
    instructor_lastname: str
    instructor_email: str
    school_district: int


class FullCourseBuildSettings(BaseCourseBuildSettings):
    course_name: str
    course_shortname: str
    course_category: int
    course_id: Optional[int] = None
    course_enrollment_url: Optional[str] = None
    course_enrollment_key: Optional[str] = None
    academic_year: str
    academic_year_short: str
    base_course_id: int
    creator: int
    status: enum.Enum
    id: int
