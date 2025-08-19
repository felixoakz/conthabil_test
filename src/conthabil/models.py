from sqlalchemy import Column, Integer, String, DateTime

from conthabil.database import Base


class Gazette(Base):
    """
    SQLAlchemy model for the 'gazettes' table.
    """
    __tablename__ = "gazettes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    publication_date = Column(DateTime, nullable=False)
