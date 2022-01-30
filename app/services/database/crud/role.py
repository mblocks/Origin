# -*- coding: utf-8 -*-
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas import RoleCreate, RoleUpdate
from app.services import redis
from ..models import Role, App
from .base import CRUDBase


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def create(self, db: Session, **kwargs) -> Optional[Role]:
        created_role = super().create(db, **kwargs)
        app = db.query(App).with_entities(App.id, App.name).filter(App.id == created_role.app_id).first()
        redis.set_role(app, created_role)
        return created_role

    def update(self, db: Session, **kwargs) -> Optional[Role]:
        updated_role = super().update(db, **kwargs)
        app = db.query(App).with_entities(App.id, App.name).filter(App.id == updated_role.app_id).first()
        redis.set_role(app, updated_role)
        return updated_role

    def delete(self, db: Session, **kwargs) -> Optional[Role]:
        affected_rows = super().delete(db, **kwargs)
        redis.del_role(kwargs['filter']['id'])
        return affected_rows

role = CRUDRole(Role)
