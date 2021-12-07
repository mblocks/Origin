# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from . import routers

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routers.welcome, tags=["welcome"])
app.include_router(routers.authorized, tags=["authorized"])
app.include_router(routers.admin_apps, tags=["admin-apps"], prefix="/admin")
app.include_router(routers.admin_users, tags=["admin-users"], prefix="/admin")
