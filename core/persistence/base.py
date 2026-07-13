"""
SQLAlchemy declarative base.

Central location for all ORM models.
"""

from sqlalchemy.orm import declarative_base  # type: ignore[import-untyped, import-not-found]

Base = declarative_base()
