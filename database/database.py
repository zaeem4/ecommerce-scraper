from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLAlchemy specific code, as with any other app
DATABASE_URL = "sqlite:///./ecom-scraper.db"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

db_engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

Base = declarative_base()
