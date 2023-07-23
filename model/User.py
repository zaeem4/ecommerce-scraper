from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer

from database.database import Base


class Users(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    password = Column(String)
