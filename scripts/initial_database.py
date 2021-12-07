import logging
from app.services.database import Base, models
from app.services.database.session import engine


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Initial database tables created")


if __name__ == "__main__":
    main()
