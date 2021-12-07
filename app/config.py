# -*- coding: utf-8 -*-
import os
import sys
from functools import lru_cache
from typing import List

from sqlalchemy.sql.expression import true
from pydantic import BaseSettings

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class Settings(BaseSettings):
    FASTAPI_CONFIG: str = 'development'
    APP_NAME: str = "Mblocks Origin"
    OPENAPI_PREFIX: str = ""
    SQLALCHEMY_DATABASE_URI: str = prefix + os.path.join(basedir, 'data.db')
    SQLALCHEMY_ECHO: bool = FASTAPI_CONFIG!='production'
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = None

    CONTAINER_NAME_PREFIX: str = 'mblocks'
    CONTAINER_NETWORK: str = 'mblocks'
    Environment: List[str] = ['FASTAPI_CONFIG','SQLALCHEMY_DATABASE_URI']
    class Config:
        case_sensitive: bool = True
        env_file: bool = ".env"


class Production(Settings):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite://///mblocks/server/main/data.db'


class Test(Settings):
    REDIS_HOST: str = '127.0.0.1'
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///test.db'


@lru_cache()
def get_settings():
    if os.getenv("FASTAPI_CONFIG") == 'test':
        return Test()
    if os.getenv("FASTAPI_CONFIG") == 'production':
        return Production()
    return Settings()
