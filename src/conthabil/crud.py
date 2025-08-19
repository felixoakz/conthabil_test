from typing import Sequence
import logging

from sqlalchemy.orm import Session
from sqlalchemy import extract

from conthabil.models import Gazette
from conthabil.schemas import GazetteCreate


def create_gazette(db: Session, gazette: GazetteCreate) -> Gazette:
    """
    Creates a new gazette entry in the database. This operation is idempotent:
    if a gazette with the same URL already exists, it returns the existing one
    without creating a duplicate.

    Args:
        db: The database session.
        gazette: The Pydantic schema for creating a gazette.

    Returns:
        The created or existing Gazette ORM object.
    """

    db_gazette = db.query(Gazette).filter(Gazette.url == gazette.url).first()

    if db_gazette:
        logging.info(f"Gazette with URL {gazette.url} already exists. Skipping creation.")
        return db_gazette

    db_gazette = Gazette(url=gazette.url, publication_date=gazette.publication_date)
    db.add(db_gazette)
    db.commit()
    db.refresh(db_gazette)
    logging.info(f"Successfully created new gazette entry for URL: {gazette.url}")

    return db_gazette


def get_gazettes(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Gazette]:
    """
    Retrieves a list of gazette entries from the database.

    Args:
        db: The database session.
        skip: The number of records to skip (for pagination).
        limit: The maximum number of records to return (for pagination).

    Returns:
        A sequence of Gazette ORM objects.
    """

    return db.query(Gazette).offset(skip).limit(limit).all()


def get_gazettes_by_month_year(db: Session, month: int, year: int) -> Sequence[Gazette]:
    """
    Retrieves gazette entries filtered by publication month and year.

    Args:
        db: The database session.
        month: The month to filter by (1-12).
        year: The year to filter by.

    Returns:
        A sequence of Gazette ORM objects matching the criteria.
    """

    return (
        db.query(Gazette)
        .filter(extract("month", Gazette.publication_date) == month)
        .filter(extract("year", Gazette.publication_date) == year)
        .all()
    )
