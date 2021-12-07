# -*- coding: utf-8 -*-
from app.schemas import RoleCreate, RoleUpdate
from ..models import Role
from .base import CRUDBase


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    pass


role = CRUDRole(Role)
