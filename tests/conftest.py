# -*- coding: utf-8 -*-
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from app.main import app
from app.services.database import Base, engine, SessionLocal  # noqa: F401


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def pytest_configure(config):
    pass


@pytest.fixture(scope="session")
def db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client() -> Generator:
    yield TestClient(app)
