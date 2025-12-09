import os
from contextlib import contextmanager
from typing import Optional

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
except Exception:  # pragma: no cover - optional dependency
    create_engine = None
    sessionmaker = None


# Database helper for PostgreSQL connections.
# Behavior:
# - If `DATABASE_URL` (or individual PG_* env vars) is provided, returns a SQLAlchemy sessionmaker.
# - If no DB config is present, functions return a no-op context manager yielding None so
#   existing code paths remain unchanged and PDF/web outputs are not affected.


def _build_database_url() -> Optional[str]:
    # Prefer full URL if set
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # Otherwise, build from components (useful for Windows environment variables)
    user = os.getenv("PGUSER") or os.getenv("POSTGRES_USER")
    password = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("PGHOST") or "localhost"
    port = os.getenv("PGPORT") or "5432"
    db = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB")

    if not (user and password and db):
        return None

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


_DATABASE_URL = _build_database_url()
_engine = None
_SessionLocal = None

if _DATABASE_URL and create_engine is not None:
    # Use pool_pre_ping to improve reliability across networked DBs
    _engine = create_engine(_DATABASE_URL, pool_pre_ping=True)
    _SessionLocal = sessionmaker(bind=_engine)


@contextmanager
def get_session():
    """Context manager yielding a SQLAlchemy session or None.

    Usage:
        with get_session() as session:
            if session is not None:
                session.execute("SELECT 1")
    """
    if _SessionLocal is None:
        # No DB configured: yield None so callers don't need to change behavior
        yield None
        return

    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_connection(timeout_seconds: int = 5) -> bool:
    """Return True if DB connection can be established and a lightweight query runs."""
    if _engine is None:
        return False
    try:
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
