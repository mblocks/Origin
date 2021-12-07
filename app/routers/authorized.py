# -*- coding: utf-8 -*-
from fastapi import APIRouter
from app.services import redis


router = APIRouter()

@router.get("/authorized")
async def get_authorized(user_id: int):
    return redis.get_authorized(user_id=user_id)
