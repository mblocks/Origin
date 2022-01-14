# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from . import routers, deps, config, backgrounds

settings = config.get_settings()
dependencies = [Depends(deps.get_current_user)] if settings.FASTAPI_CONFIG == 'test' else []
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routers.welcome, tags=["welcome"], prefix="/welcome")
app.include_router(routers.authorized, tags=["authorized"])
app.include_router(routers.settings, tags=["settings"], dependencies=dependencies)
app.include_router(routers.admin_apps, tags=["admin-apps"], prefix="/admin", dependencies=dependencies)
app.include_router(routers.admin_users, tags=["admin-users"], prefix="/admin", dependencies=dependencies)

@app.on_event("startup")
async def startup_event():
    backgrounds.init_kong()
