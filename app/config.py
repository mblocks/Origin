# -*- coding: utf-8 -*-
import os
import sys
from functools import lru_cache
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
    SQLALCHEMY_ECHO: bool = True
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = None
    SERVICES_GATEWAY_CONFIG: str =  None

    CONTAINER_NAME_PREFIX: str = 'mblocks'
    CONTAINER_NETWORK: str = 'mblocks'
    #Environment: List[str] = ['FASTAPI_CONFIG','SQLALCHEMY_DATABASE_URI']

    ROOT_NAME: str = 'admin'
    ROOT_PASSWORD: str = 'mblocks'

    VOLUMES_ROOT: str = None

    class Config:
        case_sensitive: bool = True
        env_file: bool = ".env"


class Production(Settings):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite://///data/origin/origin/data.db'
    REDIS_HOST: str = 'redis.origin.mblocks'
    SERVICES_GATEWAY_CONFIG: str = 'http://gateway.origin.mblocks:8001/config'
    SQLALCHEMY_ECHO: bool = False

class Test(Settings):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///test.db'


@lru_cache()
def get_settings():
    if os.getenv("FASTAPI_CONFIG") == 'test':
        return Test()
    if os.getenv("FASTAPI_CONFIG") == 'production' or os.getenv("VOLUMES_ROOT"):
        return Production()
    return Settings()
