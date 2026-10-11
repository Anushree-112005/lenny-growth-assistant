from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.logging import logger
from app.db.models import Base

# Setup engine with connection pool
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"connect_timeout": 5} if "postgresql" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> bool:
    """Create all tables and configure PostgreSQL full-text search indexes if available."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")

        # If PostgreSQL, create full-text search index on chunks if not exists
        if "postgresql" in settings.DATABASE_URL:
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            CREATE INDEX IF NOT EXISTS idx_chunks_fts 
                            ON transcript_chunks 
                            USING gin(to_tsvector('english', content));
                            """
                        )
                    )
                logger.info("PostgreSQL full-text search GIN index verified/created.")
            except Exception as fts_err:
                logger.warning(f"Note on FTS index creation: {fts_err}")

        return True
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> dict:
    """Check database connectivity status."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "connected", "database": settings.DATABASE_URL.split("@")[-1]}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}
