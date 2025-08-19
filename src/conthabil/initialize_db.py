import logging

from conthabil.database import engine
from conthabil.config import setup_logging
from conthabil import models


def initialize_database():
    """
    Creates all database tables defined in SQLAlchemy models.
    Sets up logging configs for the application.
    """

    setup_logging()

    logging.info("Attempting to create database tables...")

    models.Base.metadata.create_all(bind=engine)

    logging.info("Database tables created (if they didn't exist).")


if __name__ == "__main__":

    initialize_database()
