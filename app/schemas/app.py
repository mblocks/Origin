from typing import Dict, Optional, List
from pydantic import BaseModel

class NameValue(BaseModel):
    name: str
    value: str

class Environment(BaseModel):
    name: str
    value: str


class Volume(BaseModel):
    name: Optional[str] = None
    host_path: str
    mount_path: str


class Port(BaseModel):
    name: Optional[str] = None
    host_port: Optional[str] = None
    container_port: str


class Middleware(BaseModel):
    name: str
    config: Optional[Dict[str, str]] = {}


class IngressTarget(BaseModel):
    name: Optional[str] = None
    port: int
    path: str


class Ingress(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    path:  Optional[str] = None
    target: Optional[IngressTarget] = None
    middlewares: Optional[List[Middleware]] = []


class FunctionArg(BaseModel):
    name: str
    title: Optional[str] = None
    options: Optional[List[NameValue]] = []


class Function(BaseModel):
    name: str
    title: Optional[str]
    args: Optional[Dict[str, FunctionArg]] = []


class Container(BaseModel):
    id: Optional[str] = None
    short_id: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    ip: Optional[str] = None


class AppBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    path: Optional[str] = None
    enabled: Optional[bool] = True
    image: Optional[str] = None
    version: Optional[int] = None
    environment: Optional[List[Environment]] = []
    volumes: Optional[List[Volume]] = []
    command: Optional[List[str]] = []
    args:  Optional[List[str]] = []
    ports: Optional[List[Port]] = []
    ingress: Optional[List[Ingress]] = []
    parent: Optional[int] = None
    container: Optional[Container] = None
    functions: Optional[List[Function]] = []

    class Config:
        orm_mode = True


class App(AppBase):
    depends: List[AppBase] = []


class AppCreate(App):
    pass


class AppUpdate(BaseModel):
    """
    remove `name` from the update schema to protect the app name
    """
    title: Optional[str] = None
    description: Optional[str] = None
    path: Optional[str] = None
    enabled: Optional[bool] = True
    image: Optional[str] = None
    environment: Optional[List[Environment]] = []
    volumes: Optional[List[Volume]] = []
    command: Optional[List[str]] = []
    args:  Optional[List[str]] = []
    ports: Optional[List[Port]] = []
    ingress: Optional[List[Ingress]] = []
    version: Optional[int] = None
