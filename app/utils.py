# -*- coding: utf-8 -*-
import secrets
from app import services, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_random_str() -> str:
    return secrets.token_hex()

def generate_apikey(current_user:schemas.CurrentUser) -> str:
    return services.redis.generate_apikey(current_user)
