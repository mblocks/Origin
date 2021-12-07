# -*- coding: utf-8 -*-
from app.schemas import AccountCreate, AccountUpdate
from ..models import User
from .base import CRUDBase


class CRUDAccount(CRUDBase[User, AccountCreate, AccountUpdate]):
    pass


account = CRUDAccount(User)
