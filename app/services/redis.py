import time
import redis
import json
from app import utils, schemas
from app.config import get_settings

settings = get_settings()

redis_pool = redis.ConnectionPool(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT,
                                  db=settings.REDIS_DB,
                                  decode_responses=True)
client = redis.Redis(connection_pool=redis_pool)


perfix = 'redis-auth'
key_sessions = '{}:sessions'.format(perfix)
key_users = '{}:users:{}'.format(perfix, '{}')
key_users_sessions = '{}:users:{}:sessions'.format(perfix, '{}')
key_users_authorized = '{}:users:{}:authorized'.format(perfix, '{}')
key_roles = '{}:roles'.format(perfix)


def generate_apikey(current_user: schemas.CurrentUser) -> str:
    apikey = utils.generate_random_str()
    pipe = client.pipeline()
    pipe.zadd(key_sessions, {apikey: current_user.id})
    pipe.zadd(key_users_sessions.format(
        current_user.id), {apikey: time.time()})
    pipe.set(key_users.format(current_user.id), json.dumps({
        'id': current_user.id,
        'third': current_user.third if hasattr(current_user, 'third') else '',
        'third_user_id': current_user.third_user_id if hasattr(current_user, 'third_user_id') else '',
        'third_user_name': current_user.third_user_name if hasattr(current_user, 'third_user_name') else '',
    }))
    pipe.execute()
    pipe.reset()
    return apikey

def get_user(apikey):
    id = client.zscore(key_sessions, apikey)
    if not id:
        return None
    user = client.get(key_users.format(int(id)))
    return json.loads(user) if user else None


def set_authorized(user_id, app_id, roles):
    pipe = client.pipeline()
    for role_id in roles:
        pipe.zadd(key_users_authorized.format(user_id), {role_id:app_id})
    pipe.execute()
    pipe.reset()


def del_authorized(user_id):
    pass


def get_authorized(user_id, lite=True):
    apps = {}
    roles = client.zrange(key_users_authorized.format(user_id),0,-1)
    for item in client.zrange(key_roles, 0, -1):
        role = json.loads(item)
        if str(role['role_id']) not in roles:
            continue
        item_app_name = role.get('app_name')
        item_auth = role.get('auth')
        if not apps.get(item_app_name):
            apps[item_app_name] = {
                'name': item_app_name,
                'auth': {}
            }
        for item_fun, item_limit in item_auth.items():
            if not apps[item_app_name]['auth'].get(item_fun):
                apps[item_app_name]['auth'][item_fun] = []
            apps[item_app_name]['auth'][item_fun].append(item_limit)
    
    return apps


def set_role(app, role):
    client.zadd(key_roles, {json.dumps({
        'app_id': app.id,
        'app_name': app.name,
        'role_id': role.id,
        'auth': role.auth
    }):role.id})


def del_role(role_id):
    client.zremrangebyscore(key_roles,role_id,role_id)
