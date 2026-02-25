"""
Database initialization for Track Tracker.

This module creates all the tables defined in app/db/models.py
inside the PostgreSQL database. It uses the engine from session.py
and the Base metadata from models.py.

What Base.metadata.create_all() does:
    - Looks at every class that inherits from Base (Artist, Track, etc.)
    - Generates CREATE TABLE SQL for each one
    - Runs those CREATE TABLE statements against the database
    - If a table already exists, it skips it (safe to run multiple times)

Usage:
    # From the CLI
    uv run python main.py init-db

    # From Python
    from app.db.init import init_db
    init_db()
"""

import logging

from app.db.models import Base
from app.db.session import engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Create all database tables.

    This reads every SQLAlchemy model that inherits from Base
    (Artist, Track, TrackArtist, Video, VideoStat) and issues
    CREATE TABLE IF NOT EXISTS for each one.

    Safe to call multiple times — existing tables are not dropped or modified.
    """
    logger.info("Creating database tables...")

    # This is where the magic happens. Base.metadata holds the schema
    # info for all our models. create_all() turns that into real SQL
    # and executes it against the engine's database connection.
    Base.metadata.create_all(bind=engine)

    logger.info("Database tables created successfully.")
    print("✓ All database tables created successfully.")
