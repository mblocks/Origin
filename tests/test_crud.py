# -*- coding: utf-8 -*-
from app.services.database import crud
from app import schemas


def test_app_create(db):
    app = crud.app.create(db, payload=schemas.AppCreate.parse_obj(
        {
            'name': 'admin',
            'description': 'admin',
            'image': 'nginx:alpine',
            'ingress': [
                {
                    'name': 'login',
                    'path': '/login',
                    'target': {'path': '/login', 'port': 80},
                },
                {
                    'name': 'join',
                    'path': '/join',
                    'target': {'path': '/join', 'port': 80},
                },
                {
                    'name': 'index',
                    'path': '/',
                    'target': {'path': '/', 'port': 80},
                }
            ],
             "auth": {
                         "query": {
                                     "title": "arole",
                                    "conditions": [
                                        {"name": "user_id", "value": 10}
                                    ]
                                }
            },
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
                            'target': {
                                'path': '/',
                                'port': 8000,
                            }
                        },
                    ],
                    'environment': [
                        {'name': 'KONG_NGINX_HTTP_INCLUDE',
                         'value': '/usr/local/kong/nginx-custom.conf'},
                        {'name': 'LOCALDOMAIN', 'value': '127.0.0.11'},
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
                        {'name': 'REDIS_HOST',
                         'value': 'redis.admin.mblocks'},
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
            ]
        })
    )
    find_app = crud.app.get(db=db, filter={'id': app.id})
    assert find_app.name == 'admin'


def test_app_update(db):
    app = crud.app.create(db, payload=schemas.AppCreate.parse_obj(
        {
            'name': 'test_app_update',
            'description': 'admin',
            'image': 'nginx:alpine',
        }))
    crud.app.update(db,
                    filter={'id': app.id},
                    payload={
                        'name': 'test_app_update_updated',
                        'description': 'admin_updated',
                        'image': 'nginx:alpine_admin_updated',
                        'environment': [
                            {
                                'name': 'Hello',
                                'value': 'world'}
                        ]
                    })
    find_app = crud.app.get(db=db, filter={'id': app.id})
    assert find_app.name == 'test_app_update_updated'
    assert find_app.description == 'admin_updated'
    assert find_app.image == 'nginx:alpine_admin_updated'
    assert find_app.environment[0].get('name') == 'Hello'


def test_app_delete(db):
    app = crud.app.create(db, payload=schemas.AppCreate.parse_obj(
        {
            'name': 'test_app_delete',
            'description': 'admin',
            'image': 'nginx:alpine',
        }))
    crud.app.delete(db, filter={'id': app.id})
    find_app = crud.app.get(db=db, filter={'id': app.id})
    assert find_app == None


def test_account_create(db):
    account = crud.account.create(db, payload=schemas.AccountCreate.parse_obj({
        'user_name': 'test_account_create',
        'display_name': 'hello',
        'password': '123456789'
    }))

    find_account = crud.account.get(db=db, filter={'id': account.id})
    assert find_account.user_name == account.user_name


def test_account_update(db):
    account = crud.account.create(db, payload=schemas.AccountCreate.parse_obj({
        'user_name': 'test_account_update',
        'display_name': 'hello',
        'password': '123456789'
    }))

    updated_account = crud.account.update(db=db, filter={'id': account.id}, payload={
                                          'display_name': 'hello_updated'})
    assert updated_account.display_name == 'hello_updated'


def test_user_create(db):
    user = crud.user.create(db, payload=schemas.UserCreate.parse_obj({
        'user_name': 'test_user_create',
        'display_name': 'hello',
        'password': '123456789'
    }))

    find_user = crud.user.get(db=db, filter={'id': user.id})
    assert find_user.user_name == user.user_name


def test_user_update(db):
    user = crud.user.create(db, payload=schemas.UserCreate.parse_obj({
        'user_name': 'test_user_update',
        'display_name': 'hello',
        'password': '123456789'
    }))

    updated_user = crud.user.update(db=db, filter={'id': user.id}, payload={
                                    'display_name': 'hello_updated'})
    assert updated_user.display_name == 'hello_updated'


def test_role_create(db):
    role = crud.role.create(db, payload=schemas.RoleCreate.parse_obj({
        'title': 'test_role_create',
        'auth': {"query":{}},
        'app_id': 1,
    }))

    find_role = crud.role.get(db=db, filter={'id': role.id})
    assert find_role.title == role.title


def test_role_update(db):
    role = crud.role.create(db, payload={
        'title': 'test_role_update',
        'auth': {"query": {"hello": 1000}},
        'app_id': 1,
    })

    updated_role = crud.role.update(db=db,
                                    filter={'id': role.id},
                                    payload={
                                        'title': 'test_role_updated',
                                        'auth': {"query": {"hello": 2000,"world":'21'}},
                                    })
    assert updated_role.title == 'test_role_updated'


def test_authorized_set(db):
    created_app = crud.app.create(db, payload=schemas.AppCreate.parse_obj(
        {
            'name': 'test_app_authorized',
            'description': 'admin',
            'image': 'nginx:alpine',
        }))
    created_role = crud.role.create(db, payload={
        'title': 'test_role_update',
        'auth': {"query": {"hello": 1000}},
        'app_id': created_app.id
    })
    created_authorized = crud.authorized.create(db, payload=schemas.AuthorizedCreate(app_id=created_app.id,user_id=1,roles=[created_role.id]))
    assert len(created_authorized.get('roles')) == 1
