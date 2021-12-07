from typing import Optional, List
from pydantic import BaseModel


class User(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        orm_mode = True

class App(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    authorized: Optional[bool] = None


class AboutUs(BaseModel):
    logo: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    currentUser: Optional[User] = None
    apps: Optional[List[App]] = []
