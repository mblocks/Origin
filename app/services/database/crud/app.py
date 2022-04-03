# -*- coding: utf-8 -*-
from typing import List, Optional
from app.schemas import AppCreate, AppUpdate
from app.services import redis
from sqlalchemy.orm import Session
from ..models import App, Role
from .base import CRUDBase


class CRUDApp(CRUDBase[App, AppCreate, AppUpdate]):

    def create(self,
               db: Session,
               payload: AppCreate
               ) -> App:
        depends = payload.depends
        roles = payload.roles
        del payload.container
        del payload.depends
        del payload.roles
        created_app = super().create(db, payload=payload, refresh=False, commit=False)
        created_app.depends = []
        for depend in depends:
            del depend.container
            depend.parent = created_app.id
            created_depend = super().create(db, payload=depend, refresh=False, commit=False)
            created_app.depends.append(created_depend)
        for role in roles:
            role.app_id = created_app.id
            db.add(Role(**role.dict()))
        db.commit()
        """
        ignore redis sync, avoid boot container can not find redis server and fail.
        app's visibility_level default value is private， so we don't need to sync redis.
        """
        #redis.set_app(created_app)
        return created_app

    def update(self, db: Session, **kwargs) -> Optional[Role]:
        updated_app = super().update(db, **kwargs)
        redis.set_app(updated_app)
        return updated_app

    def query(
        self,
        db: Session,
        **kwargs
    ) -> List[App]:
        apps = super().query(db, **kwargs)
        if len(apps) == 0:
            return apps
        if kwargs.get('select'):
            return apps
        depends = {}
        for app in apps:
            depends[app.id] = []

        for item in super().query(db, filter={'parent in': depends.keys()}):
            depends[item.parent].append(item)
        for app in apps:
            app.depends = depends[app.id]

        return apps

    def get(self, db: Session, **kwargs) -> Optional[App]:
        app = super().get(db, **kwargs)
        if app is None:
            return app
        if kwargs.get('select'):
            return app
        app.depends = super().query(db, filter={'parent': app.id})
        return app


app = CRUDApp(App)
