from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# This creates the connection to PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# Each request gets its own database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All models will inherit from this Base
Base = declarative_base()

# This function gives a database session to each API request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()