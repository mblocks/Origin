# Import all the models, so that Base has them before being
# imported by Alembic
from .base import Base  # noqa
from .session import engine, SessionLocal
from . import crud, models  # noqa

def client():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
