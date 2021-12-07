# -*- coding: utf-8 -*-
from app.schemas import AccountCreate, AccountUpdate
from sqlalchemy.orm import Session
from ..models import User, Authorized, Role, App
from .base import CRUDBase


class CRUDUser(CRUDBase[User, AccountCreate, AccountUpdate]):

    def authorized(self, db: Session, *, user_id: int, app_id: int = None) -> list:
        authorized_exists = db.query(Authorized)\
                              .filter(Authorized.role_id == Role.id,
                                      Authorized.user_id == user_id,
                                      Authorized.app_id == app_id if app_id else Authorized.data_enabled == True,
                                      Authorized.data_enabled == True)

        query_roles = db.query(Role)\
                        .join(App, App.id == Role.app_id)\
                        .with_entities(Role.id, Role.title, Role.app_id, App.name.label('app_name'), App.title.label('app_title'))\
                        .filter(authorized_exists.exists())\
                        .filter(Role.data_enabled == True)\
                        .all()

        apps = {}
        for item in query_roles:
            print(item)
            if not apps.get(item.app_id):
                apps[item.app_id] = {
                    'id': item.app_id, 'name': item.app_name, 'title': item.app_title, 'roles': []}
            apps[item.app_id]['roles'].append(item)
        return list(apps.values())


user = CRUDUser(User)
