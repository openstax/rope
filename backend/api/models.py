from typing import Optional, Literal

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
    school_district_name: str


class FullCourseBuildSettings(BaseCourseBuildSettings):
    id: int
    course_name: str
    course_shortname: str
    course_id: Optional[int] = None
    course_enrollment_url: Optional[str] = None
    course_enrollment_key: Optional[str] = None
    academic_year: str
    academic_year_short: str
    creator_email: str
    status: Literal["created", "processing", "completed", "failed"]


class MoodleUser(BaseModel):
    first_name: str
    last_name: str
    email: str
