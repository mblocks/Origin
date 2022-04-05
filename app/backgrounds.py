import requests
from app.config import get_settings
from app.services import database, redis
from app.services.database.session import SessionLocal

settings = get_settings()

def init_kong() -> None:
    db = SessionLocal()
    kong_services = {}
    apps = database.crud.app.query(db, filter={'parent': 'None'}, skip=0, limit=1000)
    for item in apps:
        for item_router in item.ingress:
            if item_router.get('use_auth') != None:
                """
                set service name as app{id} if ingress's router named app's name
                check service has authorized when request this service
                """
                item_service_name = 'app{}{}'.format(item.id, '' if item_router.get('name') == item.name else item_router.get('name'))
                kong_services[item_service_name] = {
                                            'name':item_service_name,
                                            'app': item,
                                            'url':'http://{}.mblocks:{}{}'.format(item.name,item_router['target']['port'],item_router['target']['path']),
                                            'routes':[ {'paths':[item_router['path']]} ]
                                            }

        continue # ignore app depends ingress
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
    
    for v in kong_services.values():
        redis.set_app(v.get('app'))
        del v['app']

    config = {
        "_format_version": "2.1",
        "_transform": True,
        "services": list(kong_services.values()),
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
