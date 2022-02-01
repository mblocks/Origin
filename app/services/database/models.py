# -*- coding: utf-8 -*-
import json
from typing import TYPE_CHECKING
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.services.database.base import Base
from app.utils import get_password_hash


class App(Base):
    __tablename__ = "apps"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True)
    title = Column(String(100))
    description = Column(String(400))
    path = Column(String(100), unique=True)
    enabled = Column(Boolean, default=True)
    image = Column(String(200))
    version = Column(Integer, default=1)
    parent = Column(Integer)

    _environment = Column("environment", String(400), default='[]')
    _volumes = Column("volumes", String(400), default='[]')
    _command = Column("command", String(400), default='[]')
    _args = Column("args", String(400), default='[]')
    _ports = Column("ports", String(400), default='{}')
    _ingress = Column("ingress", String(400), default='[]')
    _functions = Column("functions", String(400), default='[]')

    @property
    def environment(self):
        return json.loads(self._environment)

    @environment.setter
    def environment(self, value):
        # https://docs.sqlalchemy.org/en/14/orm/mapped_attributes.html#using-custom-datatypes-at-the-core-level
        self._environment = json.dumps(value)

    @property
    def volumes(self):
        return json.loads(self._volumes)

    @volumes.setter
    def volumes(self, value):
        self._volumes = json.dumps(jsonable_encoder(value))

    @property
    def command(self):
        return json.loads(self._command)

    @command.setter
    def command(self, value):
        self._command = json.dumps(jsonable_encoder(value))

    @property
    def args(self):
        return json.loads(self._args)

    @args.setter
    def args(self, value):
        self._args = json.dumps(jsonable_encoder(value))

    @property
    def ports(self):
        return json.loads(self._ports)

    @ports.setter
    def ports(self, value):
        self._ports = json.dumps(jsonable_encoder(value))

    @property
    def ingress(self):
        return json.loads(self._ingress)

    @ingress.setter
    def ingress(self, value):
        self._ingress = json.dumps(jsonable_encoder(value))

    @property
    def functions(self):
        return json.loads(self._functions)

    @functions.setter
    def functions(self, value):
        self._functions = json.dumps(jsonable_encoder(value))


class Role(Base):
    __tablename__ = "apps_roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    app_id = Column(Integer, index=True)
    title = Column(String(100))
    description = Column(String(400))
    _auth = Column("auth", String(800))
    enabled = Column(Boolean, default=True)

    users = relationship("User",
                         primaryjoin="Role.id==foreign(Authorized.role_id)",
                         secondaryjoin="and_(User.id==foreign(Authorized.user_id),Authorized.data_enabled==True)",
                         secondary='authorized',
                         viewonly=True
                         )

    @property
    def auth(self):
        """
        prevent pydantic model auto translate json string to dict
        """
        return json.loads(self._auth)

    @auth.setter
    def auth(self, value):
        self._auth = json.dumps(value, ensure_ascii=False)


class Authorized(Base):
    __tablename__ = "authorized"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    role_id = Column(Integer, index=True)
    app_id = Column(Integer)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(100), unique=True, index=True)
    email = Column(String(100), index=True)
    display_name = Column(String(100))
    enabled = Column(Boolean, default=True)
    _password = Column("password", String(100))

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = get_password_hash(value)

    roles = relationship("Role",
                         primaryjoin="User.id==foreign(Authorized.user_id)",
                         secondaryjoin="and_(Role.id==foreign(Authorized.role_id),Authorized.data_enabled==True)",
                         secondary='authorized',
                         viewonly=True
                         )


class ThirdUser(Base):
    __tablename__ = "third_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    third = Column(String(100), index=True)
    third_user_id = Column(String(100), index=True)
    third_user_name = Column(String(100))
    user_id = Column(Integer)
    binded_at = Column(DateTime, default=datetime.utcnow)
