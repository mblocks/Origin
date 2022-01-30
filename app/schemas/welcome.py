from typing import Optional, List
from pydantic import BaseModel


class App(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    authorized: Optional[bool] = None


class User(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    apps: Optional[List[App]] = []
    class Config:
        orm_mode = True


class AboutUs(BaseModel):
    logo: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    userinfo: Optional[User] = None
