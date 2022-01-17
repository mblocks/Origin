from typing import Optional
from pydantic import BaseModel


class AccountLogin(BaseModel):
    user_name: str
    password: str


class AccountCreate(AccountLogin):
    display_name: Optional[str] = None
    email: Optional[str] = None


class AccountUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class AccountChangePassword(BaseModel):
    password: str
    new_password: str


class AccountInfo(BaseModel):
    user_name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
