"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from database.models import Base


def get_engine():
    """
    Create and return SQLAlchemy engine
    """
    db_path = settings.get_db_path()

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create SQLite engine
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL query logging
    )

    return engine


def get_session() -> Session:
    """
    Create and return a new database session
    """
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def init_db():
    """
    Initialize database - create all tables
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print(f"[OK] Database initialized at: {settings.get_db_path()}")


def drop_all_tables():
    """
    Drop all tables (use with caution!)
    """
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    print("[WARN]  All tables dropped")


if __name__ == "__main__":
    # Test database connection
    init_db()
    session = get_session()
    print(f"[OK] Database connection successful")
    session.close()
