from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

# Lazy engine initialization to avoid connection at import time
_engine = None

def get_engine():
    """
    Get or create SQLAlchemy engine.
    Uses lazy initialization to avoid connection at import time.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,  # Test connections before using them
            pool_size=10,
            max_overflow=20
        )
    return _engine


def get_session_local():
    """Get SessionLocal class bound to engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
