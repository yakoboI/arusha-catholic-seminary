import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db, Base
from app.main import app
from app.config import settings

# Create in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for testing"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    """Create database session for testing"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123",
        "role": "admin"
    }

@pytest.fixture
def test_student_data():
    """Test student data"""
    return {
        "admission_number": "STU001",
        "prem_number": "PREM001",
        "full_name": "Test Student",
        "date_of_birth": "2005-01-01",
        "gender": "male",
        "address": "Test Address",
        "phone": "1234567890",
        "email": "student@example.com",
        "parent_name": "Test Parent",
        "parent_phone": "0987654321",
        "student_level": "o_level",
        "class_id": 1
    }

@pytest.fixture
def test_teacher_data():
    """Test teacher data"""
    return {
        "employee_id": "TCH001",
        "full_name": "Test Teacher",
        "email": "teacher@example.com",
        "phone": "1234567890",
        "subject": "Mathematics",
        "qualification": "Bachelor's Degree",
        "hire_date": "2020-01-01",
        "salary": 50000.0,
        "status": "active"
    }

@pytest.fixture
def auth_headers(client, test_user_data):
    """Get authentication headers"""
    # Create user
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    
    # Login
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_upload_dir = settings.UPLOAD_DIR
        settings.UPLOAD_DIR = temp_dir
        yield temp_dir
        settings.UPLOAD_DIR = original_upload_dir

# Test data fixtures
@pytest.fixture
def sample_classes():
    """Sample class data"""
    return [
        {
            "name": "Form 1A",
            "level": "o_level",
            "capacity": 30,
            "academic_year": "2024",
            "room_number": "101",
            "description": "First year class"
        },
        {
            "name": "Form 2B",
            "level": "o_level",
            "capacity": 25,
            "academic_year": "2024",
            "room_number": "102",
            "description": "Second year class"
        }
    ]

@pytest.fixture
def sample_subjects():
    """Sample subject data"""
    return [
        {
            "name": "Mathematics",
            "code": "MATH",
            "description": "Advanced mathematics",
            "subject_level": "o_level"
        },
        {
            "name": "English",
            "code": "ENG",
            "description": "English language and literature",
            "subject_level": "o_level"
        },
        {
            "name": "Physics",
            "code": "PHY",
            "description": "Physical sciences",
            "subject_level": "a_level"
        }
    ]

@pytest.fixture
def sample_grades():
    """Sample grade data"""
    return [
        {
            "student_id": 1,
            "subject_id": 1,
            "class_id": 1,
            "term": "Term 1",
            "academic_year": "2024",
            "test_score": 85,
            "exam_score": 90,
            "assignment_score": 88,
            "total_score": 87.5,
            "grade": "A",
            "remarks": "Excellent performance"
        }
    ]

# Utility functions for testing
def create_test_user(db_session, user_data):
    """Create a test user in the database"""
    from app.models import User
    from app.auth import get_password_hash
    
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        hashed_password=get_password_hash(user_data["password"]),
        role=user_data["role"],
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def create_test_student(db_session, student_data):
    """Create a test student in the database"""
    from app.models import Student
    
    student = Student(**student_data)
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student

def create_test_teacher(db_session, teacher_data):
    """Create a test teacher in the database"""
    from app.models import Teacher
    
    teacher = Teacher(**teacher_data)
    db_session.add(teacher)
    db_session.commit()
    db_session.refresh(teacher)
    return teacher

# Test configuration
def pytest_configure(config):
    """Configure pytest"""
    # Set test environment
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers to tests
    for item in items:
        if "test_auth" in item.nodeid:
            item.add_marker(pytest.mark.auth)
        elif "test_students" in item.nodeid:
            item.add_marker(pytest.mark.students)
        elif "test_teachers" in item.nodeid:
            item.add_marker(pytest.mark.teachers)
        elif "test_classes" in item.nodeid:
            item.add_marker(pytest.mark.classes)
        elif "test_grades" in item.nodeid:
            item.add_marker(pytest.mark.grades) 