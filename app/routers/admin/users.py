# -*- coding: utf-8 -*-
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas
from app.services import database, redis
from app.deps import get_current_user

router = APIRouter()


@router.get("/users", response_model=schemas.UserList)
async def query_users(db: Session = Depends(database.client),
                      currentUser: schemas.CurrentUser = Depends(get_current_user),
                      user_name: Optional[str] = None,
                      email: Optional[str] = None,
                      skip: int = 0,
                      limit: int = 100,
                      total: int = None):
    filter = {'user_name': user_name, 'email': email}
    users = database.crud.user.query(db, filter=filter, skip=skip, limit=limit)
    if not total:
        total = database.crud.user.count(db, filter=filter)
    return {'total': total, 'data': users}


@router.post("/users", response_model=schemas.User)
async def create_user(payload: schemas.UserCreate,
                      currentUser: schemas.CurrentUser = Depends(get_current_user),
                      db: Session = Depends(database.client)
                      ):
    created_user = database.crud.user.create(db, payload=payload)
    return created_user


@router.get("/users/{id}", response_model=schemas.User)
async def get_user(id: int,
                   db: Session = Depends(database.client),
                   currentUser: schemas.CurrentUser = Depends(get_current_user),
                   ):
    find_user = database.crud.user.get(db, filter={'id': id})
    return find_user


@router.post("/users/{id}/delete", response_model=schemas.User)
async def delete_users(id: int,
                       db: Session = Depends(database.client),
                       currentUser: schemas.CurrentUser = Depends(get_current_user),
                       ):
    deleted_user = database.crud.user.get(db, filter={'id': id})
    database.crud.user.delete(db, filter={'id': id})
    return deleted_user


@router.post("/users/{id}", response_model=schemas.User)
async def update_user(id: int,
                      payload: schemas.UserUpdate,
                      db: Session = Depends(database.client),
                      ):
    updated_user = database.crud.user.update(
        db, filter={'id': id}, payload=payload)
    return updated_user


@router.post("/users/{user_id}/authorized/apps/{app_id}/delete")
async def delete_user_app_authorized(user_id: int,
                                     app_id: int,
                                     db: Session = Depends(database.client),
                                     ):
    database.crud.authorized.delete(
        db, filter={'user_id': user_id, 'app_id': app_id})
    return database.crud.user.authorized(db, user_id=user_id, app_id=app_id)


@router.post("/users/{user_id}/authorized/apps/{app_id}", response_model=List[schemas.UserAuthorized])
async def set_user_app_authorized(user_id: int,
                                  app_id: int,
                                  payload: List[int],
                                  db: Session = Depends(database.client),
                                  ):
    create_authorized = schemas.AuthorizedCreate(user_id=user_id, app_id=app_id, roles=payload)
    updated_authorized = database.crud.authorized.update(db, payload=create_authorized)
    redis.set_authorized(**updated_authorized)
    return database.crud.user.authorized(db, user_id=user_id, app_id=app_id)


@router.get("/users/{user_id}/authorized/apps", response_model=List[schemas.UserAuthorized])
async def get_user_apps_authorized(user_id: int,
                                   app_id: int = None,
                                   ignore: bool = False,
                                   db: Session = Depends(database.client),
                                   ):
    return database.crud.user.authorized(db, user_id=user_id, app_id=app_id, ignore=ignore)
