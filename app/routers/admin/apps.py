# -*- coding: utf-8 -*-
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas
from app.services import docker, database
router = APIRouter()


@router.get("/apps", response_model=List[schemas.App])
async def query_apps(db: Session = Depends(database.client)):
    # query all apps from database
    apps = database.crud.app.query(db, filter={'parent': 'None'})
    # query all apps from container
    containers = docker.query_container()
    # sync app's container
    for item in apps:
        item.container = containers.get(
            '{}-{}'.format(item.name, item.version))
        for item_depend in item.depends:
            item_depend.container = containers.get(
                '{}-{}-{}'.format(item.name, item_depend.name, item_depend.version))
    return apps


@router.post("/apps", response_model=schemas.App)
async def deploy_app(payload: schemas.AppCreate,
                     db: Session = Depends(database.client)
                     ):
    created_app = database.crud.app.create(db, payload=payload)
    docker.deploy_app(created_app)
    return created_app


@router.post("/apps/{id}", response_model=schemas.App)
async def update_app(id: int,
                     payload: schemas.AppUpdate,
                     db: Session = Depends(database.client)):
    app = database.crud.app.get(
        db, select=['version', 'parent'], filter={'id': id})
    payload.version = app.version + 1
    updated_app = database.crud.app.update(
        db, filter={'id': id}, payload=payload)
    if app.parent:
        parent = database.crud.app.get(
            db, select=['name'], filter={'id': app.parent})
    else:
        parent = None
    docker.update_app(app=updated_app, parent=parent.name if parent else None)
    return updated_app


@router.post("/apps/{id}/delete", response_model=schemas.App)
async def delete_app(id: int, db: Session = Depends(database.client)):
    app = database.crud.app.get(db, filter={'id': id})
    if app.parent:
        parent = database.crud.app.get(
            db, select=['name'], filter={'id': app.parent})
    else:
        parent = None
        for depend in app.depends:
            database.crud.app.remove(
                db, filter={'id': depend.id}, commit=False)
    database.crud.app.remove(db, filter={'id': id}, commit=False)
    db.commit()
    docker.remove_app(app=app, parent=parent.name if parent else None)
    return app


@router.get("/apps/{id}/roles", response_model=schemas.RoleList)
async def query_app_roles(id: int,
                          db: Session = Depends(database.client),
                          title: Optional[str] = None,
                          skip: int = 0,
                          limit: int = 100,
                          total: int = None):
    filter = {'id': id, 'title': title}
    roles = database.crud.role.query(db, filter=filter, skip=skip, limit=limit)
    if not total:
        total = database.crud.role.count(db, filter=filter)
    return {'total': total, 'data': roles}


@router.post("/apps/{app_id}/roles", response_model=schemas.Role)
async def create_app_role(payload: schemas.RoleCreate,
                          app_id: int,
                          db: Session = Depends(database.client)):
    payload.app_id = app_id
    created_role = database.crud.role.create(db, payload=payload)
    return created_role


@router.post("/apps/{app_id}/roles/{role_id}", response_model=schemas.Role)
async def update_app_role(payload: schemas.RoleUpdate,
                          app_id: int,
                          role_id: int,
                          db: Session = Depends(database.client)):
    created_role = database.crud.role.update(
        db, filter={'app_id': app_id, 'id': role_id}, payload=payload)
    return created_role


@router.post("/apps/{app_id}/roles/{role_id}/delete", response_model=schemas.Role)
async def delete_app_roles(app_id: int,
                           role_id: int,
                           db: Session = Depends(database.client),
                           ):
    deleted_role = database.crud.role.get(
        db, filter={'app_id': app_id, 'id': role_id})
    database.crud.role.delete(db, filter={'app_id': app_id, 'id': role_id})
    return deleted_role
