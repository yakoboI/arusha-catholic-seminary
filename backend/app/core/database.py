"""
Database Configuration Module
Centralized database management for Arusha Catholic Seminary
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine with proper configuration
def create_database_engine():
    """Create database engine with appropriate configuration"""
    try:
        if settings.DATABASE_URL.startswith("sqlite"):
            # SQLite configuration
            engine = create_engine(
                settings.DATABASE_URL,
                echo=settings.DATABASE_ECHO,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False}
            )
        else:
            # PostgreSQL/MySQL configuration
            engine = create_engine(
                settings.DATABASE_URL,
                echo=settings.DATABASE_ECHO,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_pre_ping=True,
                pool_recycle=3600
            )
        
        logger.info(f"Database engine created successfully: {settings.DATABASE_URL}")
        return engine
    
    except Exception as e:
        logger.error(f"Failed to create database engine: {str(e)}")
        raise


# Create database engine
engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Yields a database session and ensures it's closed
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions
    Use this for manual database operations
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database context error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


def drop_tables():
    """Drop all database tables (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {str(e)}")
        raise


def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False


def get_database_info() -> dict:
    """Get database information"""
    try:
        with get_db_context() as db:
            if settings.DATABASE_URL.startswith("sqlite"):
                # SQLite specific info
                result = db.execute("PRAGMA database_list")
                databases = result.fetchall()
                
                result = db.execute("PRAGMA table_list")
                tables = result.fetchall()
                
                return {
                    "type": "SQLite",
                    "databases": [{"name": db[1], "file": db[2]} for db in databases],
                    "tables": [{"name": table[1], "type": table[2]} for table in tables],
                    "url": settings.DATABASE_URL
                }
            else:
                # PostgreSQL/MySQL specific info
                result = db.execute("SELECT version()")
                version = result.scalar()
                
                return {
                    "type": "PostgreSQL/MySQL",
                    "version": version,
                    "url": settings.DATABASE_URL
                }
    except Exception as e:
        logger.error(f"Failed to get database info: {str(e)}")
        return {"error": str(e)}


# Database health check
def health_check() -> dict:
    """Database health check for monitoring"""
    try:
        connection_ok = check_database_connection()
        info = get_database_info()
        
        return {
            "status": "healthy" if connection_ok else "unhealthy",
            "connection": connection_ok,
            "info": info,
            "timestamp": "2024-01-01T00:00:00Z"  # Replace with actual timestamp
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"  # Replace with actual timestamp
        }
