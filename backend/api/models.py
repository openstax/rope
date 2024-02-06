from pydantic import BaseModel


class GoogleLoginData(BaseModel):
    token: str


class PostSessionResponse(BaseModel):
    email: str
    is_manager: bool
    is_admin: bool


class GetUsersResponse(BaseModel):
    id: int
    email: str
    is_manager: bool
    is_admin: bool


class GetCurrentUserResponse(BaseModel):
    email: str
    is_manager: bool
    is_admin: bool


class PostUserRequest(BaseModel):
    email: str
    is_manager: bool
    is_admin: bool


class PostUserResponse(BaseModel):
    id: int
    email: str
    is_manager: bool
    is_admin: bool


class PutUserRequest(BaseModel):
    id: int
    email: str
    is_manager: bool
    is_admin: bool


class PutUserResponse(BaseModel):
    id: int
    email: str
    is_manager: bool
    is_admin: bool


class DeletedUserResponse(BaseModel):
    message: str


class DeletedSessionResponse(BaseModel):
    message: str
