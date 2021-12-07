from typing import Optional
from pydantic import BaseModel


class AccountLogin(BaseModel):
    user_name: str
    password: str


class AccountCreate(AccountLogin):
    display_name: Optional[str] = None
    email: Optional[str] = None


class AccountUpdate(BaseModel):
    pass


class AccountChangePassword(BaseModel):
    password: str
    new_password: str


