import logging
import socket
from app import schemas
from app.services import docker
from app.config import get_settings
from app.services.database.session import SessionLocal
from app.services.database import crud, models


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

def init() -> None:
    db = SessionLocal()
    if crud.account.count(db, filter={}) == 0:
        crud.account.create(db, payload=schemas.AccountCreate.parse_obj({
            'user_name': settings.ROOT_NAME,
            'display_name': settings.ROOT_NAME,
            'password': settings.ROOT_PASSWORD,
        }))
    if crud.app.count(db, filter={}) == 0:
        create_origin_app(db)


def create_origin_app(db) -> None:
    created_app = crud.app.create(db, payload=schemas.AppCreate.parse_obj(
        {
            'name': 'origin',
            'description': '',
            'image': 'mblocks/origin',
            'ingress': [
                {
                    'name': 'welcome',
                    'path': '/api/welcome',
                    'target': {'path': '/welcome', 'port': 80},
                },
                {
                    'name': 'default',
                    'path': '/',
                    'use_auth': True,
                    'target': {'path': '/', 'port': 80},
                },
            ],
            'depends': [
                {
                    'name': 'redis',
                    'title': 'redis',
                    'image': 'redis:alpine',
                },
                {
                    'name': 'gateway',
                    'title': 'gateway',
                    'image': 'mblocks/gateway:0.0.18',
                    'ingress': [
                        {
                            'name': 'api',
                            'path': '/api',
                            'target': {'path': '/', 'port': 8000}
                        },
                    ],
                    'environment': [
                        {'name': 'KONG_DATABASE', 'value': 'off'},
                        {'name': 'KONG_PROXY_ACCESS_LOG',
                         'value': '/dev/stdout'},
                        {'name': 'KONG_PROXY_ERROR_LOG',
                         'value': '/dev/stdout'},
                        {'name': 'KONG_ADMIN_ACCESS_LOG',
                         'value': '/dev/stdout'},
                        {'name': 'KONG_ADMIN_ERROR_LOG',
                         'value': '/dev/stdout'},
                        {'name': 'KONG_ADMIN_LISTEN',
                         'value': '0.0.0.0:8001'},
                        {'name': 'KONG_PLUGINS',
                         'value': 'bundled,redis-auth'},
                    ]
                },
                {
                    'name': 'traefik',
                    'image': 'traefik:v2.4',
                    'ports': [
                        {'name': 'http', 'container_port': 8080, 'host_port': 8080},
                        {'name': 'http', 'container_port': 80, 'host_port': 80}
                    ],
                    'volumes': [
                        {
                            'name': 'docker',
                            'mount_path': '/var/run/docker.sock',
                            'host_path': '/var/run/docker.sock',
                            '/var/run/docker.sock': '/var/run/docker.sock'
                        },
                    ],
                    'command': [
                        "--api.insecure=true",
                        "--providers.docker=true",
                        "--providers.docker.exposedbydefault=false",
                        "--entrypoints.web.address=:80"
                    ]
                }
            ],
            'roles': [
                { 'title':'admin', 'auth': {} }
            ]
        })
    )
    rename_container(docker.get_container_name(app_name=created_app.name,version=created_app.version))
    docker.deploy_app(created_app)

def rename_container(name):
    hostname = socket.gethostname()
    docker.rename_container(hostname, name)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
