import logging
from app.services import database, redis
from app.services.database.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_redis():
    db = SessionLocal()
    query_roles = database.crud.role.query(db, filter={}, skip=0, limit=1000)
    query_apps = database.crud.app.query(db, select=['id','name'],filter={'parent': 'None'}, skip=0, limit=1000)
    apps = {}
    for item in query_apps:
        apps[item.id] = item
    for item in query_roles:
        redis.set_role(app=apps[item.app_id], role=item)
    query_authorized = database.crud.authorized.query(db, filter={}, skip=0, limit=100000)
    for item in query_authorized:
        redis.set_authorized(user_id=item.user_id,app_id=item.app_id,roles=[item.role_id])


def main() -> None:
    logger.info("Creating initial redis")
    init_redis()
    logger.info("Initial redis created")


if __name__ == "__main__":
    main()
