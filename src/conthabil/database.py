import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import get_settings


# Get database URL from environment variable
DATABASE_URL = get_settings().DATABASE_URL

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency to get a database session for FastAPI.
    Ensures the session is closed after the request.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
