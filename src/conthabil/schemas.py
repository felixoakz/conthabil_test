from datetime import datetime

from pydantic import BaseModel


class GazetteBase(BaseModel):
    """
    Base Pydantic schema for Gazette, containing common fields.
    """
    url: str
    publication_date: datetime


class GazetteCreate(GazetteBase):
    """
    Pydantic schema for creating a new Gazette entry.
    Inherits from GazetteBase.
    """
    pass


class GazetteResponse(GazetteBase):
    """
    Pydantic schema for returning Gazette data.
    Inherits from GazetteBase and adds the 'id'.
    Configures ORM mode for easy conversion from SQLAlchemy models.
    """
    id: int

    class Config:
        from_attributes = True
