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


class MoodleUser(BaseModel):
    first_name: str
    last_name: str
    email: str
