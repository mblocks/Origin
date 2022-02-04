import requests
from app.config import get_settings
from app.services import database, redis
from app.services.database.session import SessionLocal

settings = get_settings()

def init_kong() -> None:
    db = SessionLocal()
    kong_services = []
    apps = database.crud.app.query(db, filter={'parent': 'None'}, skip=0, limit=1000)
    for item in apps:
        for item_router_index, item_router in  enumerate(item.ingress):
            if item_router.get('use_auth') != None:
                kong_services.append({'name':'{}-{}'.format(item.name, item_router_index),
                                    'url':'http://{}.mblocks:{}{}'.format(item.name,item_router['target']['port'],item_router['target']['path']),
                                    'routes':[
                                            {'paths':[item_router['path']]}
                                        ]
                                    })
            
        for item_depend in item.depends:
            for item_depend_router_index, item_depend_router in  enumerate(item_depend.ingress):
                if item_depend_router.get('use_auth') != None:
                    kong_services.append({'name':'{}-{}-{}'.format(item.name, item_depend.name, item_depend_router_index),
                                        'url':'http://{}.{}.mblocks:{}{}'.format(item_depend.name, item.name ,item_depend_router['target']['port'],item_depend_router['target']['path']),
                                        'routes':[
                                                {'paths':[item_depend_router['path']]}
                                            ]
                                        })
    
    if len(kong_services) == 0:
        print('=== kong config 0 services===')
        return
    
    config = {
        "_format_version": "2.1",
        "_transform": True,
        "services": kong_services,
        "plugins": [
            {
                "name": "redis-auth",
                "config": {
                    "hide_credentials": True,
                    "redis_host": 'redis.origin.mblocks',
                        "redis_key_prefix": "redis-auth:",
                        "consumer_keys": ["id", "third", "third_user_id", "third_user_name", "is_admin"],
                }
            }
        ]
    }
    print('=== kong config {} services==='.format(len(kong_services)))
    if settings.SERVICES_GATEWAY_CONFIG:
        requests.post(settings.SERVICES_GATEWAY_CONFIG, json=config)


def init_redis_data():
    db = SessionLocal()
    query_roles = database.crud.role.query(db, filter={}, skip=0, limit=1000)
    query_apps = database.crud.app.query(db, select=['id','name'],filter={'parent': 'None'}, skip=0, limit=1000)
    apps = {}
    for item in query_apps:
        apps[item.id] = item
    for item in query_roles:
        redis.set_role(app=apps[item.app_id], role=item)
    print('=== redis data init ===')
    query_authorized = database.crud.authorized.query(db, filter={}, skip=0, limit=100000)
    for item in query_authorized:
        redis.set_authorized(user_id=item.user_id,app_id=item.app_id,roles=[item.role_id])
    print('=== redis data authorized init ===')
