# -*- coding: utf-8 -*-
from fastapi import Request


def get_user(request: Request):
    return {
        'id': request.headers.get('x-consumer-id'),
        'third': request.headers.get('x-consumer-third'),
        'third_user_id': request.headers.get('x-consumer-third-user-id'),
        'third_user_name': request.headers.get('x-consumer-third-user-name', '').encode("Latin-1").decode("utf-8")
    }
