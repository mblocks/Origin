from typing import Optional, List
from pydantic import BaseModel


class RoleBase(BaseModel):
    app_id: Optional[int] = None
    title: Optional[str] = None
    auth: Optional[dict] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None

    class Config:
        orm_mode = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class Role(RoleBase):
    id: Optional[int] = None


class RoleList(BaseModel):
    data: List[Role]
    total: Optional[int] = 0
