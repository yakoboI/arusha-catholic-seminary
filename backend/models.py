#!/usr/bin/env python3
"""
Arusha Catholic Seminary - Database Models
SQLAlchemy models for all school entities
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./school_management.db")

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# ============================================================================
# USER MODELS
# ============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # admin, teacher, student, parent
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    students = relationship("Student", back_populates="user")
    teachers = relationship("Teacher", back_populates="user")

# ============================================================================
# SCHOOL ENTITY MODELS
# ============================================================================

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    student_number = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)  # Male, Female
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    grade = Column(String(10), nullable=False)  # 10A, 11B, 12A, etc.
    enrollment_date = Column(Date, default=datetime.utcnow().date())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")
    grades = relationship("Grade", back_populates="student")

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    employee_number = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    subject = Column(String(50), nullable=False)
    experience_years = Column(Integer, default=0)
    qualification = Column(String(100), nullable=True)
    hire_date = Column(Date, default=datetime.utcnow().date())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="teachers")
    classes = relationship("Class", back_populates="teacher")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, index=True, nullable=False)  # 10A, 11B, 12A
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    capacity = Column(Integer, default=30)
    current_students = Column(Integer, default=0)
    academic_year = Column(String(10), nullable=False)  # 2024-2025
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="classes")

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)  # MATH101, ENG101
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    credits = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)  # present, absent, late, excused
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="attendances")

class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    term = Column(String(20), nullable=False)  # Term 1, Term 2, Term 3
    academic_year = Column(String(10), nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0)
    grade_letter = Column(String(2), nullable=True)  # A, B, C, D, F
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject")

class NonTeachingStaff(Base):
    __tablename__ = "non_teaching_staff"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_number = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    position = Column(String(100), nullable=False)  # Secretary, Janitor, etc.
    department = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    hire_date = Column(Date, default=datetime.utcnow().date())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Parent(Base):
    __tablename__ = "parents"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    relationship = Column(String(20), nullable=False)  # Father, Mother, Guardian
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    occupation = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Alumni(Base):
    __tablename__ = "alumni"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    grade_at_graduation = Column(String(10), nullable=True)
    current_occupation = Column(String(100), nullable=True)
    company = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Donor(Base):
    __tablename__ = "donors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # Individual, Organization, Corporate
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    total_donations = Column(Float, default=0.0)
    last_donation_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# DATABASE UTILITIES
# ============================================================================

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def seed_initial_data():
    """Seed initial data for the application"""
    db = SessionLocal()
    try:
        # Check if admin user exists
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@arushaseminary.edu",
                full_name="System Administrator",
                hashed_password=pwd_context.hash("admin123"),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created successfully")
        
        # Seed sample data if tables are empty
        if db.query(Student).count() == 0:
            # Add sample students
            students = [
                Student(
                    student_number="STU001",
                    first_name="John",
                    last_name="Doe",
                    date_of_birth=datetime(2008, 5, 15).date(),
                    gender="Male",
                    grade="10A",
                    phone="+255123456789",
                    email="john.doe@student.edu"
                ),
                Student(
                    student_number="STU002",
                    first_name="Jane",
                    last_name="Smith",
                    date_of_birth=datetime(2007, 8, 22).date(),
                    gender="Female",
                    grade="11B",
                    phone="+255123456790",
                    email="jane.smith@student.edu"
                ),
                Student(
                    student_number="STU003",
                    first_name="Mike",
                    last_name="Johnson",
                    date_of_birth=datetime(2006, 3, 10).date(),
                    gender="Male",
                    grade="12A",
                    phone="+255123456791",
                    email="mike.johnson@student.edu"
                )
            ]
            db.add_all(students)
            
            # Add sample teachers
            teachers = [
                Teacher(
                    employee_number="TCH001",
                    first_name="Dr. Johnson",
                    last_name="Mathematics",
                    date_of_birth=datetime(1980, 1, 15).date(),
                    gender="Male",
                    subject="Mathematics",
                    experience_years=10,
                    qualification="PhD Mathematics",
                    phone="+255123456792",
                    email="dr.johnson@teacher.edu"
                ),
                Teacher(
                    employee_number="TCH002",
                    first_name="Ms. Williams",
                    last_name="English",
                    date_of_birth=datetime(1985, 6, 20).date(),
                    gender="Female",
                    subject="English",
                    experience_years=8,
                    qualification="Masters in English",
                    phone="+255123456793",
                    email="ms.williams@teacher.edu"
                ),
                Teacher(
                    employee_number="TCH003",
                    first_name="Mr. Brown",
                    last_name="Science",
                    date_of_birth=datetime(1982, 12, 5).date(),
                    gender="Male",
                    subject="Science",
                    experience_years=12,
                    qualification="Masters in Physics",
                    phone="+255123456794",
                    email="mr.brown@teacher.edu"
                )
            ]
            db.add_all(teachers)
            
            # Add sample classes
            classes = [
                Class(name="10A", capacity=30, current_students=25, academic_year="2024-2025"),
                Class(name="11B", capacity=30, current_students=22, academic_year="2024-2025"),
                Class(name="12A", capacity=30, current_students=20, academic_year="2024-2025")
            ]
            db.add_all(classes)
            
            # Add sample subjects
            subjects = [
                Subject(code="MATH101", name="Mathematics", description="Advanced Mathematics", credits=4),
                Subject(code="ENG101", name="English", description="English Language and Literature", credits=3),
                Subject(code="SCI101", name="Science", description="General Science", credits=4),
                Subject(code="HIST101", name="History", description="World History", credits=3),
                Subject(code="GEO101", name="Geography", description="Physical and Human Geography", credits=3)
            ]
            db.add_all(subjects)
            
            db.commit()
            print("✅ Sample data seeded successfully")
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🗄️ Creating database tables...")
    create_tables()
    print("🌱 Seeding initial data...")
    seed_initial_data()
    print("✅ Database setup complete!")
