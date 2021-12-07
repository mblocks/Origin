from typing import Optional, List
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int] = None
    user_name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        orm_mode = True


class UserList(BaseModel):
    data: List[User]
    total: Optional[int] = 0


class UserCreate(User):
    pass


class UserUpdate(User):
    pass


class CurrentUser(BaseModel):
    id: Optional[int] = None
    third: Optional[str] = None
    third_user_id: Optional[str] = None
    third_user_name: Optional[str] = None


class Role(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None


class UserAuthorized(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    title: Optional[str] = None
    roles: Optional[List[Role]] = []
