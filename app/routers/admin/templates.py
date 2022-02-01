# -*- coding: utf-8 -*-
from typing import List
from fastapi import APIRouter
from app import schemas
router = APIRouter()


@router.get("/templates", response_model=List[schemas.App])
async def query_templates():
    return [
        {'name': 'hellonginx9', 'title': 'nginx', 'description': 'hello nginx', 'image': 'nginx:alpine'},
    ]
