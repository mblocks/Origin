import logging
import socket
from app import schemas
from app.services import docker
from app.config import get_settings
from app.services.database.session import SessionLocal
from app.services.database import crud


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
                    'stripprefix': '/api',
                    'target': {'path': '/welcome', 'port': 80},
                },
                {
                    'name': 'default',
                    'path': '/',
                    'use_auth': {},
                    'target': {'path': '/', 'port': 80},
                },
            ],
            'volumes': [
                {
                    'name': 'docker',
                    'mount_path': '/var/run/docker.sock',
                    'host_path': '/var/run/docker.sock',
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
                    'image': 'mblocks/gateway',
                    'ingress': [
                        {
                            'name': 'api',
                            'path': '/api',
                            'stripprefix': '/api',
                            'target': {'path': '/', 'port': 8000}
                        },
                        {
                            'name': 'default',
                            'path': '/',
                            'target': {'path': '/', 'port': 80},
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
