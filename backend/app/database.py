from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for development (easier setup) or PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./arusha_seminary.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all database tables (for testing)"""
    Base.metadata.drop_all(bind=engine)

def migrate_database():
    """Migrate database schema for existing tables"""
    with engine.connect() as connection:
        # Check if passport_photo column exists in users table
        try:
            result = connection.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            # Add passport_photo column if it doesn't exist
            if 'passport_photo' not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN passport_photo TEXT"))
                print("Added passport_photo column to users table")
            
            # Add seminary_logo column if it doesn't exist
            if 'seminary_logo' not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN seminary_logo TEXT"))
                print("Added seminary_logo column to users table")
            
            # Check students table for new columns
            result = connection.execute(text("PRAGMA table_info(students)"))
            student_columns = [row[1] for row in result.fetchall()]
            
            # Add full_name column if it doesn't exist
            if 'full_name' not in student_columns:
                connection.execute(text("ALTER TABLE students ADD COLUMN full_name TEXT"))
                print("Added full_name column to students table")
            
            # Add student_level column if it doesn't exist
            if 'student_level' not in student_columns:
                connection.execute(text("ALTER TABLE students ADD COLUMN student_level TEXT"))
                print("Added student_level column to students table")
            
            connection.commit()
            print("Database migration completed successfully")
            
        except Exception as e:
            print(f"Migration error: {e}")
            connection.rollback() 