import logging
from typing import Generator
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("foodverse.database")
logging.basicConfig(level=logging.INFO)

ACTIVE_DB_ENGINE = "in_memory"
engine = None


class Base(DeclarativeBase):
    """Base class for declarative models."""
    pass


class DummySession:
    """In-memory dummy session for compatibility."""
    def add(self, *args, **kwargs): pass
    def commit(self): pass
    def rollback(self): pass
    def refresh(self, *args, **kwargs): pass
    def close(self): pass
    def query(self, *args, **kwargs): return self
    def count(self): return 0
    def filter(self, *args, **kwargs): return self
    def first(self): return None
    def all(self): return []


def SessionLocal():
    return DummySession()


def get_db() -> Generator[DummySession, None, None]:
    """FastAPI dependency yielding in-memory session stub."""
    session = DummySession()
    try:
        yield session
    finally:
        session.close()


def get_db_info() -> dict:
    """Return runtime status indicating active in-memory operational state."""
    return {
        "engine": "in_memory",
        "is_alive": True,
        "db_name": "foodverse (in-memory)",
        "db_host": "local",
        "db_port": None,
        "is_fallback": False,
    }


def init_db():
    """No-op initialization without external database connections or disk writes."""
    logger.info("Database initialized in memory-only mode (external store removed).")
