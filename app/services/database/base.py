from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    __name__: str
    # Generate __tablename__ automatically

    data_enabled = Column(Boolean, default=True)
    data_created_at = Column(DateTime,default=datetime.utcnow)
    data_updated_at = Column(DateTime,onupdate=datetime.utcnow)
    data_deleted_at = Column(DateTime)
    data_created_by = Column(Integer)
    data_updated_by = Column(Integer)
    data_deleted_by = Column(Integer)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
