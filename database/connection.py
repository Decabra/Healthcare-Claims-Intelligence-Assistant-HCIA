"""
Database connection management
Enterprise-grade connection pooling for Postgres
"""

from contextlib import contextmanager
from typing import Generator
import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import structlog

logger = structlog.get_logger()


class DatabaseManager:
    """Manages database connections with connection pooling"""
    
    def __init__(self):
        self.engine: Engine = None
        self.SessionLocal: sessionmaker = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database connection"""
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://claims_user:claims_password@localhost:5432/claims_db"
        )
        
        # Connection pool settings
        pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Verify connections before using
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info("Database connection initialized", pool_size=pool_size, max_overflow=max_overflow)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_engine(self) -> Engine:
        """Get SQLAlchemy engine"""
        return self.engine
    
    def close(self):
        """Close all database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()

