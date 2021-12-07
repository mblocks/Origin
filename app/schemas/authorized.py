from typing import List, Optional
from pydantic import BaseModel


class AuthorizedCreate(BaseModel):
    app_id: int = None
    user_id: Optional[int] = None
    roles: List[int] = []


class AuthorizedUpdate(BaseModel):
    pass


class Role(BaseModel):
    id: int
    name: str
    description: str


class Authorized(BaseModel):
    app_id: int = None
    user_id: Optional[int] = None
    roles: List[Role] = []
