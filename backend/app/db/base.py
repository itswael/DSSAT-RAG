"""Database initialization and base models."""
from typing import Any

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    # Optional: Add common columns to all models
    pass


class TimestampMixin:
    """Mixin to add timestamp columns to models."""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def init_db(app: Any = None) -> None:
    """Initialize database models."""
    # Models are imported in main.py to ensure they're registered
    pass
