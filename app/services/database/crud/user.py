# -*- coding: utf-8 -*-
from app.schemas import AccountCreate, AccountUpdate
from sqlalchemy.orm import Session
from ..models import User, Authorized, Role, App
from .base import CRUDBase


class CRUDUser(CRUDBase[User, AccountCreate, AccountUpdate]):

    def authorized(self, db: Session, *, user_id: int, app_id: int = None, ignore: bool = False) -> list:
        authorized_exists = db.query(Authorized)\
                              .filter(Authorized.role_id == Role.id,
                                      Authorized.user_id == user_id,
                                      Authorized.app_id == app_id if app_id else Authorized.data_enabled == True,
                                      Authorized.data_enabled == True)

        query_roles = db.query(Role)\
                        .join(App, App.id == Role.app_id)\
                        .with_entities(Role.id, Role.title, Role.app_id, App.name.label('app_name'), App.title.label('app_title'))\
                        .filter(authorized_exists.exists())\
                        .filter(Role.data_enabled == True, App.data_enabled == True)\
                        .all()
        query_apps = db.query(App)\
                       .with_entities(App.id, App.title, App.name)\
                       .filter(App.parent == None, App.data_enabled == True)
        apps = {}
        for item in query_apps:
            if not apps.get(item.id):
                apps[item.id] = {'id': item.id, 'name': item.name,
                                 'title': item.title, 'roles': []}
        for item in query_roles:
            apps[item.app_id]['roles'].append(item)

        if ignore:
            return list(apps.values())
        return [item for item in apps.values() if len(item['roles']) > 0]


user = CRUDUser(User)
