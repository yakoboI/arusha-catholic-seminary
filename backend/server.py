#!/usr/bin/env python3
"""
Arusha Catholic Seminary - Complete School Management System Server
Database-integrated solution with full CRUD operations
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import json
import uuid
import re
import uvicorn

# Import our modules
from models import get_db, create_tables, seed_initial_data
from models import User, Student, Teacher, Class, Subject, Attendance, Grade, NonTeachingStaff, Parent, Alumni, Donor
from schemas import *

# ============================================================================
# CONFIGURATION
# ============================================================================

SECRET_KEY = "arusha-seminary-secret-key-2024-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security = HTTPBearer()

# File-based storage
USERS_FILE = "users.json"
PASSWORD_RESET_FILE = "password_resets.json"

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

# Create tables and seed data on startup
create_tables()
seed_initial_data()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_password_resets():
    """Load password reset tokens from JSON file"""
    if os.path.exists(PASSWORD_RESET_FILE):
        try:
            with open(PASSWORD_RESET_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_password_resets(resets):
    """Save password reset tokens to JSON file"""
    with open(PASSWORD_RESET_FILE, 'w') as f:
        json.dump(resets, f, indent=2)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Arusha Catholic Seminary API", 
    version="1.0.0",
    description="Complete School Management System API with Authentication"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Arusha Catholic Seminary School Management System",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "login": "/api/v1/auth/login",
            "register": "/api/v1/auth/register",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Arusha Catholic Seminary API is running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login_user(login: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint"""
    # Validate input
    if not login.username or not login.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    # Authenticate user
    user = authenticate_user(db, login.username, login.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": login.username})
    refresh_token = create_refresh_token(data={"sub": login.username})
    
    return LoginResponse(
        success=True,
        message="Login successful",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }
    )

@app.post("/api/v1/auth/register", response_model=RegisterResponse)
async def register_user(register: RegisterRequest):
    """User registration endpoint"""
    # Validate input
    if not register.username or not register.email or not register.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All fields are required"
        )
    
    if register.password != register.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate password strength
    is_valid, message = validate_password(register.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Validate email format
    if not validate_email(register.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Check if user already exists
    users = load_users()
    if register.username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    for user in users.values():
        if user["email"] == register.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    new_user = {
        "id": f"user-{uuid.uuid4().hex[:8]}",
        "username": register.username,
        "email": register.email,
        "full_name": register.full_name,
        "hashed_password": pwd_context.hash(register.password),
        "role": "user",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    users[register.username] = new_user
    save_users(users)
    
    return RegisterResponse(
        success=True,
        message="Registration successful",
        data={
            "user": {
                "id": new_user["id"],
                "username": new_user["username"],
                "email": new_user["email"],
                "full_name": new_user["full_name"],
                "role": new_user["role"]
            }
        }
    )

@app.post("/api/v1/auth/forgot-password", response_model=GenericResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """Forgot password endpoint"""
    users = load_users()
    
    # Find user by email
    user = None
    for u in users.values():
        if u["email"] == request.email:
            user = u
            break
    
    if not user:
        # Don't reveal if email exists or not
        return GenericResponse(
            success=True,
            message="If the email exists, a password reset link has been sent"
        )
    
    # Generate reset token
    reset_token = uuid.uuid4().hex
    resets = load_password_resets()
    resets[reset_token] = {
        "username": user["username"],
        "email": user["email"],
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
    }
    save_password_resets(resets)
    
    # In a real application, send email here
    # For now, just return success
    return GenericResponse(
        success=True,
        message="If the email exists, a password reset link has been sent"
    )

@app.post("/api/v1/auth/reset-password", response_model=GenericResponse)
async def reset_password(request: ResetPasswordRequest):
    """Reset password endpoint"""
    # Validate input
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate password strength
    is_valid, message = validate_password(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Verify reset token
    resets = load_password_resets()
    reset_data = resets.get(request.token)
    
    if not reset_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    expires_at = datetime.fromisoformat(reset_data["expires_at"])
    if datetime.now() > expires_at:
        # Remove expired token
        del resets[request.token]
        save_password_resets(resets)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Update user password
    users = load_users()
    username = reset_data["username"]
    
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    users[username]["hashed_password"] = pwd_context.hash(request.new_password)
    save_users(users)
    
    # Remove used token
    del resets[request.token]
    save_password_resets(resets)
    
    return GenericResponse(
        success=True,
        message="Password reset successful"
    )

@app.post("/api/v1/auth/refresh", response_model=GenericResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token endpoint"""
    payload = verify_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    users = load_users()
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new access token
    new_access_token = create_access_token(data={"sub": username})
    
    return GenericResponse(
        success=True,
        message="Token refreshed successfully",
        data={"access_token": new_access_token}
    )

@app.post("/api/v1/auth/logout", response_model=GenericResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """User logout endpoint"""
    # In a real application, you might want to blacklist the token
    # For now, we'll just return success
    return GenericResponse(
        success=True,
        message="Logout successful"
    )

@app.get("/api/v1/auth/me", response_model=GenericResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return GenericResponse(
        success=True,
        message="User information retrieved successfully",
        data={
            "user": {
                "id": current_user["id"],
                "username": current_user["username"],
                "email": current_user["email"],
                "full_name": current_user["full_name"],
                "role": current_user["role"],
                "is_active": current_user["is_active"],
                "created_at": current_user["created_at"],
                "last_login": current_user["last_login"]
            }
        }
    )

@app.put("/api/v1/auth/profile", response_model=GenericResponse)
async def update_profile(
    profile: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    users = load_users()
    username = current_user["username"]
    
    # Update fields if provided
    if profile.full_name is not None:
        users[username]["full_name"] = profile.full_name
    
    if profile.email is not None:
        # Check if email is already taken by another user
        for u in users.values():
            if u["username"] != username and u["email"] == profile.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
        users[username]["email"] = profile.email
    
    save_users(users)
    
    return GenericResponse(
        success=True,
        message="Profile updated successfully",
        data={
            "user": {
                "id": users[username]["id"],
                "username": users[username]["username"],
                "email": users[username]["email"],
                "full_name": users[username]["full_name"],
                "role": users[username]["role"]
            }
        }
    )

@app.put("/api/v1/auth/change-password", response_model=GenericResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    users = load_users()
    username = current_user["username"]
    
    # Verify current password
    if not verify_password(password_data.current_password, users[username]["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Validate password strength
    is_valid, message = validate_password(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Update password
    users[username]["hashed_password"] = pwd_context.hash(password_data.new_password)
    save_users(users)
    
    return GenericResponse(
        success=True,
        message="Password changed successfully"
    )

# ============================================================================
# SCHOOL MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/v1/students", response_model=StudentListResponse)
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all students with pagination and filtering"""
    query = db.query(Student).filter(Student.is_active == True)
    
    if search:
        query = query.filter(
            (Student.first_name.contains(search)) |
            (Student.last_name.contains(search)) |
            (Student.student_number.contains(search))
        )
    
    if grade:
        query = query.filter(Student.grade == grade)
    
    total = query.count()
    students = query.offset(skip).limit(limit).all()
    
    return StudentListResponse(
        success=True,
        data=students,
        total=total,
        message=f"Retrieved {len(students)} students"
    )

@app.get("/api/v1/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get a specific student by ID"""
    student = db.query(Student).filter(Student.id == student_id, Student.is_active == True).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/api/v1/students", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student"""
    # Check if student number already exists
    existing_student = db.query(Student).filter(Student.student_number == student.student_number).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student number already exists")
    
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.put("/api/v1/students/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student: StudentUpdate, db: Session = Depends(get_db)):
    """Update a student"""
    db_student = db.query(Student).filter(Student.id == student_id, Student.is_active == True).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = student.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/api/v1/students/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student (soft delete)"""
    db_student = db.query(Student).filter(Student.id == student_id, Student.is_active == True).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db_student.is_active = False
    db.commit()
    return {"success": True, "message": "Student deleted successfully"}

@app.get("/api/v1/teachers", response_model=TeacherListResponse)
async def get_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all teachers with pagination and filtering"""
    query = db.query(Teacher).filter(Teacher.is_active == True)
    
    if search:
        query = query.filter(
            (Teacher.first_name.contains(search)) |
            (Teacher.last_name.contains(search)) |
            (Teacher.employee_number.contains(search))
        )
    
    if subject:
        query = query.filter(Teacher.subject == subject)
    
    total = query.count()
    teachers = query.offset(skip).limit(limit).all()
    
    return TeacherListResponse(
        success=True,
        data=teachers,
        total=total,
        message=f"Retrieved {len(teachers)} teachers"
    )

@app.get("/api/v1/teachers/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Get a specific teacher by ID"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id, Teacher.is_active == True).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@app.post("/api/v1/teachers", response_model=TeacherResponse)
async def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    """Create a new teacher"""
    # Check if employee number already exists
    existing_teacher = db.query(Teacher).filter(Teacher.employee_number == teacher.employee_number).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="Employee number already exists")
    
    db_teacher = Teacher(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@app.put("/api/v1/teachers/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(teacher_id: int, teacher: TeacherUpdate, db: Session = Depends(get_db)):
    """Update a teacher"""
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id, Teacher.is_active == True).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    update_data = teacher.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_teacher, field, value)
    
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@app.delete("/api/v1/teachers/{teacher_id}")
async def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Delete a teacher (soft delete)"""
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id, Teacher.is_active == True).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    db_teacher.is_active = False
    db.commit()
    return {"success": True, "message": "Teacher deleted successfully"}

@app.get("/api/v1/classes", response_model=ClassListResponse)
async def get_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all classes with pagination and filtering"""
    query = db.query(Class).filter(Class.is_active == True)
    
    if search:
        query = query.filter(Class.name.contains(search))
    
    if academic_year:
        query = query.filter(Class.academic_year == academic_year)
    
    total = query.count()
    classes = query.offset(skip).limit(limit).all()
    
    return ClassListResponse(
        success=True,
        data=classes,
        total=total,
        message=f"Retrieved {len(classes)} classes"
    )

@app.get("/api/v1/classes/{class_id}", response_model=ClassResponse)
async def get_class(class_id: int, db: Session = Depends(get_db)):
    """Get a specific class by ID"""
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_obj

@app.post("/api/v1/classes", response_model=ClassResponse)
async def create_class(class_data: ClassCreate, db: Session = Depends(get_db)):
    """Create a new class"""
    # Check if class name already exists
    existing_class = db.query(Class).filter(Class.name == class_data.name).first()
    if existing_class:
        raise HTTPException(status_code=400, detail="Class name already exists")
    
    db_class = Class(**class_data.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@app.put("/api/v1/classes/{class_id}", response_model=ClassResponse)
async def update_class(class_id: int, class_data: ClassUpdate, db: Session = Depends(get_db)):
    """Update a class"""
    db_class = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    update_data = class_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_class, field, value)
    
    db.commit()
    db.refresh(db_class)
    return db_class

@app.delete("/api/v1/classes/{class_id}")
async def delete_class(class_id: int, db: Session = Depends(get_db)):
    """Delete a class (soft delete)"""
    db_class = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    db_class.is_active = False
    db.commit()
    return {"success": True, "message": "Class deleted successfully"}

@app.get("/api/v1/attendance", response_model=AttendanceListResponse)
async def get_attendance(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: Optional[int] = Query(None),
    date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get attendance data with filtering"""
    query = db.query(Attendance)
    
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    
    if date:
        query = query.filter(Attendance.date == date)
    
    total = query.count()
    attendance_records = query.offset(skip).limit(limit).all()
    
    return AttendanceListResponse(
        success=True,
        data=attendance_records,
        total=total,
        message=f"Retrieved {len(attendance_records)} attendance records"
    )

@app.post("/api/v1/attendance", response_model=AttendanceResponse)
async def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """Create attendance record"""
    db_attendance = Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@app.get("/api/v1/subjects", response_model=SubjectListResponse)
async def get_subjects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all subjects with pagination and filtering"""
    query = db.query(Subject).filter(Subject.is_active == True)
    
    if search:
        query = query.filter(
            (Subject.name.contains(search)) |
            (Subject.code.contains(search))
        )
    
    total = query.count()
    subjects = query.offset(skip).limit(limit).all()
    
    return SubjectListResponse(
        success=True,
        data=subjects,
        total=total,
        message=f"Retrieved {len(subjects)} subjects"
    )

@app.post("/api/v1/subjects", response_model=SubjectResponse)
async def create_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    """Create a new subject"""
    # Check if subject code already exists
    existing_subject = db.query(Subject).filter(Subject.code == subject.code).first()
    if existing_subject:
        raise HTTPException(status_code=400, detail="Subject code already exists")
    
    db_subject = Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@app.get("/api/v1/grades", response_model=GradeListResponse)
async def get_grades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    term: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get grades with filtering"""
    query = db.query(Grade)
    
    if student_id:
        query = query.filter(Grade.student_id == student_id)
    
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    
    if term:
        query = query.filter(Grade.term == term)
    
    total = query.count()
    grades = query.offset(skip).limit(limit).all()
    
    return GradeListResponse(
        success=True,
        data=grades,
        total=total,
        message=f"Retrieved {len(grades)} grades"
    )

@app.post("/api/v1/grades", response_model=GradeResponse)
async def create_grade(grade: GradeCreate, db: Session = Depends(get_db)):
    """Create a new grade"""
    db_grade = Grade(**grade.dict())
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade

@app.get("/api/v1/result-formulas")
async def get_result_formulas():
    """Get result formulas data (mock data)"""
    return [
        {"id": 1, "name": "Standard Formula", "formula": "A=90-100, B=80-89, C=70-79, D=60-69, F=0-59"},
        {"id": 2, "name": "Weighted Formula", "formula": "Tests(40%) + Assignments(30%) + Participation(30%)"}
    ]

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("Starting Arusha Catholic Seminary School Management System")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Default admin login: admin / admin123")
    print("Frontend URL: http://localhost:3000")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
