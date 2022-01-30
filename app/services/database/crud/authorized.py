# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.schemas import AuthorizedCreate, AuthorizedUpdate
from app.services import redis
from ..models import Authorized
from .base import CRUDBase


class CRUDAuthorized(CRUDBase[Authorized, AuthorizedCreate, AuthorizedUpdate]):
    def create(self,
               db: Session,
               payload: AuthorizedCreate
               ) -> AuthorizedCreate:
        return self.update(db, payload)

    def update(self, db: Session, payload: AuthorizedUpdate) -> None:
        query_authorized = super().query(
            db, filter={'app_id': payload.app_id, 'user_id': payload.user_id})
        exists_authorized = []
        for item in query_authorized:
            if item.role_id in payload.roles:
                exists_authorized.append(item.role_id)
            else:
                db.delete(item)
        for role_id in payload.roles:
            if role_id not in exists_authorized:
                db.add(Authorized(user_id=payload.user_id,
                       app_id=payload.app_id, role_id=role_id))
        db.commit()
        updated_authorized = super().query(db, filter={'app_id': payload.app_id, 'user_id': payload.user_id})
        roles = [item.role_id for item in updated_authorized]
        redis.set_authorized(app_id=payload.app_id, user_id=payload.user_id, roles=roles)
        return {'app_id': payload.app_id, 'user_id': payload.user_id, 'roles':roles}

    
authorized = CRUDAuthorized(Authorized)
