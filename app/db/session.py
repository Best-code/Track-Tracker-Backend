"""
Database engine and session management for Track Tracker.

This module creates the SQLAlchemy engine (the connection to PostgreSQL)
and a session factory that the rest of the app uses to talk to the database.

How it works:
    1. DATABASE_URL is read from environment variables
    2. An Engine is created — this is SQLAlchemy's connection pool to Postgres
    3. A SessionLocal factory is created — call it to get a new Session
    4. get_db() is a generator that FastAPI uses as a dependency to inject
       a session into route handlers, and auto-close it when the request ends

Usage in FastAPI routes:
    from app.db.session import get_db

    @app.get("/tracks")
    def get_tracks(db: Session = Depends(get_db)):
        tracks = db.query(Track).all()
        return tracks

Usage in scripts (ingestion, CLI):
    from app.db.session import SessionLocal

    with SessionLocal() as session:
        session.add(some_object)
        session.commit()
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Read the database connection string from environment variables.
# Falls back to the docker-compose defaults if DATABASE_URL isn't set.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://tracker:tracker_password@localhost:5432/track_tracker",
)

# The Engine is SQLAlchemy's connection pool.
# - pool_pre_ping=True: before handing out a connection, SQLAlchemy sends
#   a lightweight "SELECT 1" to make sure the connection is still alive.
#   This prevents crashes from stale connections after Postgres restarts.
# - echo=False: set to True if you want to see every SQL statement printed
#   to the console (useful for debugging, noisy in production).
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

# SessionLocal is a factory — every time you call SessionLocal(), you get
# a brand new Session object. Think of a Session as a "workspace" where you
# can query, add, update, and delete rows, then commit them all at once.
#
# - autocommit=False: you control when commits happen (the standard pattern)
# - autoflush=False: SQLAlchemy won't auto-flush pending changes before queries.
#   This gives you more predictable behavior — you flush/commit explicitly.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request.

    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    The session is automatically closed when the request finishes,
    even if an exception occurs (the finally block guarantees this).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
