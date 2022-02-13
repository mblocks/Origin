import os
import logging
import socket
from app import schemas
from app.services import docker
from app.config import get_settings
from app.services.database.session import SessionLocal
from app.services.database import crud


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
hostname = socket.gethostname()
origin_container = docker.get_container(name=hostname)
settings = get_settings()
volumes_root = settings.VOLUMES_ROOT

def init() -> None:
    db = SessionLocal()
    if crud.account.count(db, filter={}) == 0:
        crud.account.create(db, payload=schemas.AccountCreate.parse_obj({
            'user_name': settings.ROOT_NAME,
            'display_name': settings.ROOT_NAME,
            'password': settings.ROOT_PASSWORD,
        }))
        create_authorized = schemas.AuthorizedCreate(user_id=1, app_id=1, roles=[1])
        crud.authorized.add(db, payload=create_authorized)
        create_origin_app(db)

def is_boot() -> bool:
    return origin_container and settings.CONTAINER_NAME_PREFIX not in origin_container.name

def get_origin_settings() -> dict:
    origin_settings = {
        'environment':[],
        'volumes':[]
        }
    if is_boot():
        for k,v in settings:
            if os.getenv(k) == v and v != None:
                origin_settings['environment'].append({'name':k, 'value':v})
        for item_volume in origin_container.attrs['HostConfig']['Binds']:
            item_host_path, item_mount_path = item_volume.split(':')
            origin_settings['volumes'].append({'host_path':item_host_path, 'mount_path':item_mount_path})
        if volumes_root:
            origin_settings['volumes'].append({'host_path':volumes_root, 'mount_path':'/data'})
    return origin_settings

def create_origin_app(db) -> None:
    origin_settings = get_origin_settings()
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
                    'middlewares':[
                        {'name':'stripprefix', 'config':{'stripprefix':'/api'}},
                    ]
                },
                {
                    'name': 'default',
                    'path': '/',
                    'use_auth': {},
                    'target': {'path': '/', 'port': 80},
                },
            ],
            'volumes': origin_settings.get('volumes'),
            'environment': origin_settings.get('environment'),
            'depends': [
                {
                    'name': 'redis',
                    'title': 'redis',
                    'image': 'redis:alpine',
                    #'volumes': [{'host_path':'{}/origin/redis/data'.format(volumes_root), 'mount_path':'/data'}] if (volumes_root and len(origin_settings.get('volumes'))==0) else [],
                },
                {
                    'name': 'gateway',
                    'title': 'gateway',
                    'image': 'mblocks/gateway',
                    'ingress': [
                        {
                            'name': 'api',
                            'path': '/api',
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
    if is_boot():
        docker.remove_container(filters={'name': hostname})

def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
