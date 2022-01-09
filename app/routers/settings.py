# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from app import deps, schemas

router = APIRouter()


@router.get("/whoami")
async def whoami(current_user: schemas.CurrentUser = Depends(deps.get_current_user)):
    return {
        'userinfo': {
            'display_name': current_user.display_name,
            'apps': [{'name': 'admin', 'title': 'admin site'}],
        }
    }
