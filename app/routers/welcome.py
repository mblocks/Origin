# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.services import database, get_user
from app.utils import verify_password, generate_apikey
router = APIRouter()


@router.post("/login", response_model=schemas.AboutUs)
async def login(response: Response,
                payload: schemas.AccountLogin,
                db: Session = Depends(database.client)):
    find_user = database.crud.account.get(
        db, filter={'user_name': payload.user_name})
    if not find_user:
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "user_name"],
                "msg": "user_name is not exists",
                "type": "value_error"
            },
        ])
    if not verify_password(payload.password, find_user.password):
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "password"],
                "msg": "password is correct",
                "type": "value_error"
            },
        ])
    response.set_cookie(key="apikey", value=generate_apikey(find_user))
    return {'currentUser': find_user}


@router.post("/join", response_model=schemas.AboutUs)
async def join(response: Response,
               payload: schemas.AccountCreate,
               db: Session = Depends(database.client)):
    if database.crud.account.count(db, filter={'user_name': payload.user_name}) > 0:
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "user_name"],
                "msg": "user_name already registered",
                "type": "value_error"
            },
        ])
    account = database.crud.account.create(db=db, payload=payload)
    response.set_cookie(key="apikey", value=generate_apikey(account))
    return {'currentUser': account}


@router.get("/", response_model=schemas.AboutUs)
async def index():
    return {
        'logo': 'https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg',
        'title': 'Mblocks',
        'description': 'Hello Mblocks',
    }
