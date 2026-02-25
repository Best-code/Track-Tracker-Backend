"""
DB layer for Track Tracker.

Provides database schemas, engine/session management, and query utilities.

Key exports:
    - engine: The SQLAlchemy engine (connection pool to PostgreSQL)
    - SessionLocal: Session factory — call SessionLocal() to get a new session
    - get_db: FastAPI dependency that yields a session per request
    - Base: Declarative base for all ORM models
    - init_db: Creates all tables in the database
"""

from app.db.session import SessionLocal, engine, get_db
from app.db.models import Base

__all__ = ["SessionLocal", "engine", "get_db", "Base"]
