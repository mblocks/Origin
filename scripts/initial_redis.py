import logging
from app.services import database, redis
from app.services.database.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_redis():
    db = SessionLocal()
    query_roles = database.crud.role.query(db, filter={}, skip=0, limit=1000)
    query_apps = database.crud.app.query(db, select=['id','name','visibility_level'],filter={'parent': 'None'}, skip=0, limit=1000)
    apps = {}
    for item in query_apps:
        apps[item.id] = item
        redis.set_app(item)
    for item in query_roles:
        redis.set_role(app=apps[item.app_id], role=item)
    query_authorized = database.crud.authorized.query(db, filter={}, skip=0, limit=100000)
    authorized = {}
    for item in query_authorized:
        if item.app_id not in authorized:
            authorized[item.app_id] = {}
        if item.user_id not in authorized[item.app_id]:
            authorized[item.app_id][item.user_id] = []
        authorized[item.app_id][item.user_id].append(item.role_id)
    for app_id, user_roles in authorized.items():
        for user_id, roles in user_roles.items():
            redis.set_authorized(app_id=app_id, user_id=user_id, roles=roles)



def main() -> None:
    logger.info("Creating initial redis")
    init_redis()
    logger.info("Initial redis created")


if __name__ == "__main__":
    main()
