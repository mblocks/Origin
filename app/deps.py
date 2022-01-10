# -*- coding: utf-8 -*-
from fastapi import Request, HTTPException
from app import services, schemas


def get_current_user(request: Request):
    # request from gateway
    if request.headers.get('x-consumer-id'):
        return schemas.CurrentUser(id=request.headers.get('x-consumer-id'),
                                   third=request.headers.get(
                                       'x-consumer-third'),
                                   third_user_id=request.headers.get(
                                       'x-consumer-third-user-id'),
                                   third_user_name=request.headers.get(
                                       'x-consumer-third-user-name', '').encode("Latin-1").decode("utf-8"),
                                   )
    # direct request from client for debug test
    if request.cookies.get('apikey'):
        user = services.redis.get_user(request.cookies.get('apikey'))
        return schemas.CurrentUser(id=user.get('id'),
                                   third=user.get('third'),
                                   third_user_id=user.get('third_user_id'),
                                   third_user_name=user.get('third_user_name')
                                   )
    raise HTTPException(status_code=401, detail="apikey is invalid")
