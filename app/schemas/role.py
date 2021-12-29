from typing import Optional, List, Dict, Union
from enum import Enum
from pydantic import BaseModel, Json


class OperateEnum(str, Enum):
    eq = '='
    neq = '!='
    gt = '>'
    lt = '<'
    ge = '>='
    le = '<='
    range = 'in'


class AuthCondition(BaseModel):
    name: str
    title: Optional[str] = None
    operate: Optional[OperateEnum] = '='
    value: Union[int, str]


class AuthGroup(BaseModel):
    title: Optional[str] = None
    conditions: List[AuthCondition] = None


class RoleBase(BaseModel):
    app_id: Optional[int] = None
    title: Optional[str] = None
    auth: Optional[Dict[str, AuthGroup]] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None

    class Config:
        orm_mode = True


class RoleCreate(RoleBase):
    auth: Dict[str, AuthGroup] = {}


class RoleUpdate(RoleCreate):
    pass


class Role(RoleBase):
    id: Optional[int] = None


class RoleList(BaseModel):
    data: List[Role]
    total: Optional[int] = 0
