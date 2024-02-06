from pydantic import BaseModel


class GoogleLoginData(BaseModel):
    token: str


class BaseUser(BaseModel):
    email: str
    is_manager: bool
    is_admin: bool


class FullUser(BaseModel):
    id: int
