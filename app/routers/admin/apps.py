# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.services import docker, database
router = APIRouter()


@router.get("/apps", response_model=schemas.AppList)
async def query_apps(db: Session = Depends(database.client),
                     id: Optional[int] = None,
                     name: Optional[str] = None,
                     title: Optional[str] = None,
                     current: Optional[int] = 1,
                     page_size: Optional[int] = 10,
                    ):
    # query all apps from database
    filter = {'parent': 'None','id': id, 'name': name, 'title': title}
    apps = database.crud.app.query(db, filter=filter, skip=(current-1)*page_size, limit=page_size)
    total = database.crud.app.count(db, filter=filter)
    # query all apps from container
    containers = docker.query_container()
    # sync app's container
    for item in apps:
        item.container = containers.get(
            '{}-{}'.format(item.name, item.version))
        for item_depend in item.depends:
            item_depend.container = containers.get(
                '{}-{}-{}'.format(item.name, item_depend.name, item_depend.version))

    return { 'data': apps, 'total': total }


@router.post("/apps", response_model=schemas.App)
async def deploy_app(payload: schemas.AppCreate,
                     db: Session = Depends(database.client)
                     ):
    find_exists_app = database.crud.app.get(db, filter={'name':payload.name, 'parent': 'None'})
    if find_exists_app:
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "name"],
                "msg": 'name {} has exists'.format(payload.name),
                "type": "value_error"
            },
        ])
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

@router.post("/apps/{id}/depends", response_model=schemas.App)
async def deploy_app_depends(payload: schemas.AppCreate,
                             id: int,
                             db: Session = Depends(database.client)):
    app = database.crud.app.get(db, filter={'id': id})
    payload.parent = app.id
    created_depend = database.crud.app.create(db, payload=payload)
    docker.update_app(created_depend, app.name)
    return created_depend


@router.post("/apps/{id}/depends/{depend_id}", response_model=schemas.App)
async def update_app_depends(payload: schemas.AppUpdate,
                             id: int,
                             depend_id: int,
                             db: Session = Depends(database.client),
                            ):
    app = database.crud.app.get(db, filter={'id': id})
    depend = database.crud.app.get(db, filter={'id': depend_id})
    payload.version = depend.version + 1
    updated_depend = database.crud.app.update(db, filter={'id': depend_id}, payload=payload)
    docker.update_app(updated_depend, app.name)
    return updated_depend


@router.post("/apps/{id}/depends/{depend_id}/delete", response_model=schemas.App)
async def delete_app_depends(id: int,
                             depend_id: int,
                             db: Session = Depends(database.client),
                            ):
    app = database.crud.app.get(db, filter={'id': id})
    depend = database.crud.app.get(db, filter={'id': depend_id})
    database.crud.app.remove(db, filter={'id': depend_id})
    docker.remove_app(depend, app.name)
    return depend


@router.get("/apps/{app_id}/roles", response_model=schemas.RoleList)
async def query_app_roles(app_id: int,
                          db: Session = Depends(database.client),
                          title: Optional[str] = None,
                          id: Optional[int] = None,
                          skip: int = 0,
                          limit: int = 100,
                          total: int = None):
    filter = {'app_id': app_id, 'title': title, 'id': id}
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
    updated_role = database.crud.role.update(
        db, filter={'app_id': app_id, 'id': role_id}, payload=payload)
    return updated_role


@router.post("/apps/{app_id}/roles/{role_id}/delete", response_model=schemas.Role)
async def delete_app_roles(app_id: int,
                           role_id: int,
                           db: Session = Depends(database.client),
                           ):
    deleted_role = database.crud.role.get(
        db, filter={'app_id': app_id, 'id': role_id})
    database.crud.role.delete(db, filter={'app_id': app_id, 'id': role_id})
    return deleted_role
