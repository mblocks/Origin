# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app import deps, schemas
from app.services import database, redis
from app.utils import verify_password


router = APIRouter()


@router.get("/userinfo", response_model=schemas.AboutUs)
@router.get("/welcome", response_model=schemas.AboutUs)
async def aboutus(currentUser: schemas.CurrentUser = Depends(deps.get_current_user),
                  db: Session = Depends(database.client)):
    about_us = {
        'logo': 'https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg',
        'title': 'Mblocks',
        'description': 'Hello Mblocks',   
    }
    if currentUser is None:
        return about_us
    find_user = database.crud.account.get(db, filter={'id': currentUser.id})
    authorized = redis.get_authorized(user_id=currentUser.id)
    about_us['userinfo'] = {
        'display_name': find_user.display_name or find_user.user_name,
        'apps':({ 'name': item } for item in authorized.keys())
    }
    return about_us


@router.get("/logout")
async def logout(redirect: str = '/'):
    response = RedirectResponse(redirect)
    response.delete_cookie('apikey')
    return response


@router.get("/settings/userinfo", response_model=schemas.AccountInfo)
async def get_userinfo(currentUser: schemas.CurrentUser = Depends(deps.get_current_user),
                       db: Session = Depends(database.client)):
    find_user = database.crud.account.get(db, filter={'id': currentUser.id})
    return {
        'user_name': find_user.user_name,
        'display_name': find_user.display_name,
        'email': find_user.email,
    }


@router.post("/settings/userinfo", response_model=schemas.AccountInfo)
async def update_userinfo(payload: schemas.AccountUpdate,
                          currentUser: schemas.CurrentUser = Depends(
                              deps.get_current_user),
                          db: Session = Depends(database.client)):
    updated_user = database.crud.user.update(
        db, filter={'id': currentUser.id}, payload=payload)
    return {
        'user_name': updated_user.user_name,
        'display_name': updated_user.display_name,
        'email': updated_user.email,
    }


@router.post("/settings/security/password")
async def update_password(payload: schemas.AccountChangePassword,
                          currentUser: schemas.CurrentUser = Depends(
                              deps.get_current_user),
                          db: Session = Depends(database.client)):
    find_user = database.crud.account.get(db, filter={'id': currentUser.id})

    if not verify_password(payload.password, find_user.password):
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "password"],
                "msg": "password is correct",
                "type": "value_error"
            },
        ])
    updated_user = database.crud.user.update(
        db, filter={'id': currentUser.id}, payload={'password': payload.new_password})
    return {
        'user_name': updated_user.user_name,
        'display_name': updated_user.display_name,
        'email': updated_user.email,
    }
