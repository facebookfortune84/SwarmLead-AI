"""
Database session management.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.persistence.base import Base


def get_db_url() -> str:
    """
    Resolve database URL.

    Environment:

        SWARM_DB_URL

    Falls back to SQLite for local development.
    """

    url = os.getenv("SWARM_DB_URL")

    if url:
        return url

    db_dir = Path(os.getenv("SWARM_DB_DIR", Path(__file__).resolve().parents[2] / "data"))

    db_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    db_path = db_dir / "swarmlead.db"

    return f"sqlite:///{db_path.as_posix()}"


DATABASE_URL = get_db_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    FastAPI dependency.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def init_db():
    """
    Initialize all loaded models.
    """

    Base.metadata.create_all(bind=engine)
