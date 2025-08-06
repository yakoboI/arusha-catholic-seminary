from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, date, timedelta
import os
import shutil
from .database import get_db
from .models import User, Student, Teacher, NonTeachingStaff, Class, Subject, SubjectTeacher, Grade, Attendance, Fee, Payment, Event, Alumni, Donor, Donation, StudentResult, StudentResultDetail, TeacherAssignment, ExaminationMark, ResultFormula
from .auth import (
    get_current_active_user, authenticate_user, create_access_token, 
    get_password_hash, require_admin, require_teacher_or_admin, verify_token
)
import uuid

# Import monitoring routes
# from .routes.monitoring import router as monitoring_router

# Import file management routes
# from .file_management import file_router

# Import email management routes
# from .email_management import email_router

# Import report management routes
# from .report_management import report_router

# Import calendar management routes
# from .calendar_management import calendar_router

# Import search management routes
# from .search_management import search_router

# Import data export routes
# from .data_export import export_router

router = APIRouter()

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: str = "student"
    passport_photo: Optional[str] = None
    seminary_logo: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    passport_photo: Optional[str]
    seminary_logo: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class StudentCreate(BaseModel):
    student_id: str
    admission_number: str
    prem_number: str
    full_name: str
    date_of_birth: date
    gender: str
    address: str
    phone: str
    parent_name: str
    parent_phone: str
    class_id: Optional[int] = None
    student_level: str  # "O-Level" or "A-Level"

class StudentResponse(BaseModel):
    id: int
    student_id: str
    admission_number: str
    prem_number: str
    full_name: str
    date_of_birth: date
    gender: str
    address: str
    phone: str
    parent_name: str
    parent_phone: str
    admission_date: date
    class_id: Optional[int]
    student_level: str

    class Config:
        from_attributes = True

class TeacherCreate(BaseModel):
    employee_id: str
    full_name: str
    department: str
    qualification: str
    phone: str
    address: str

class TeacherResponse(BaseModel):
    id: int
    employee_id: str
    full_name: str
    department: str
    qualification: str
    hire_date: date
    phone: str
    address: str

    class Config:
        from_attributes = True

class NonTeachingStaffCreate(BaseModel):
    employee_id: str
    full_name: str
    department: str
    position: str
    phone: str
    address: str
    salary: Optional[float] = None

class NonTeachingStaffResponse(BaseModel):
    id: int
    employee_id: str
    full_name: str
    department: str
    position: str
    hire_date: date
    phone: str
    address: str
    salary: Optional[float]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ClassCreate(BaseModel):
    name: str
    teacher_id: Optional[int] = None
    capacity: int = 30
    academic_year: str

class ClassResponse(BaseModel):
    id: int
    name: str
    teacher_id: Optional[int]
    capacity: int
    academic_year: str
    is_active: bool

    class Config:
        from_attributes = True

class GradeCreate(BaseModel):
    student_id: int
    subject_id: int
    score: float
    semester: str
    academic_year: str

class GradeResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    score: float
    grade_letter: str
    semester: str
    academic_year: str
    created_at: datetime

    class Config:
        from_attributes = True

class AttendanceCreate(BaseModel):
    student_id: int
    class_id: int
    date: date
    is_present: bool = True
    reason: Optional[str] = None

class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    class_id: int
    date: date
    is_present: bool
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Alumni Pydantic models
class AlumniCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    graduation_year: int
    class_name: str
    current_occupation: Optional[str] = None
    employer: Optional[str] = None
    address: Optional[str] = None
    achievements: Optional[str] = None

class AlumniResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    graduation_year: int
    class_name: str
    current_occupation: Optional[str]
    employer: Optional[str]
    address: Optional[str]
    achievements: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Donor Pydantic models
class DonorCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    donor_type: str
    address: Optional[str] = None

class DonorResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    organization: Optional[str]
    donor_type: str
    address: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Donation Pydantic models
class DonationCreate(BaseModel):
    donor_id: int
    amount: float
    donation_date: date
    purpose: Optional[str] = None
    payment_method: Optional[str] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None

class DonationResponse(BaseModel):
    id: int
    donor_id: int
    amount: float
    donation_date: date
    purpose: Optional[str]
    payment_method: Optional[str]
    receipt_number: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Subject Teacher Models
class SubjectTeacherCreate(BaseModel):
    subject_id: int
    teacher_id: int
    academic_year: str

class SubjectTeacherResponse(BaseModel):
    id: int
    subject_id: int
    teacher_id: int
    academic_year: str
    is_active: bool
    created_at: datetime
    subject_name: Optional[str] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True

# Student Result Models
class StudentResultDetailCreate(BaseModel):
    subject_id: int
    subject_teacher_id: int
    score: float
    grade_letter: str
    remarks: Optional[str] = None

class StudentResultCreate(BaseModel):
    student_id: int
    academic_year: str
    term: str
    total_subjects: int
    total_score: float
    average_score: float
    position_in_class: Optional[int] = None
    total_students_in_class: Optional[int] = None
    remarks: Optional[str] = None
    date_issued: date
    result_details: List[StudentResultDetailCreate]

class StudentResultDetailResponse(BaseModel):
    id: int
    result_id: int
    subject_id: int
    subject_teacher_id: int
    score: float
    grade_letter: str
    remarks: Optional[str]
    subject_name: Optional[str] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True

class StudentResultResponse(BaseModel):
    id: int
    student_id: int
    academic_year: str
    term: str
    total_subjects: int
    total_score: float
    average_score: float
    position_in_class: Optional[int]
    total_students_in_class: Optional[int]
    remarks: Optional[str]
    date_issued: date
    issued_by: int
    created_at: datetime
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    result_details: List[StudentResultDetailResponse] = []

    class Config:
        from_attributes = True

# Teacher Assignment Models
class TeacherAssignmentCreate(BaseModel):
    teacher_id: int
    subject_id: int
    class_id: int
    academic_year: str
    term: str

class TeacherAssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    subject_id: int
    class_id: int
    academic_year: str
    term: str
    is_active: bool
    created_at: datetime
    teacher_name: Optional[str] = None
    subject_name: Optional[str] = None
    class_name: Optional[str] = None

    class Config:
        from_attributes = True

# Examination Mark Models
class ExaminationMarkCreate(BaseModel):
    assignment_id: int
    student_id: int
    test_type: str
    test_date: date
    score: float
    max_score: float = 100.0
    weight: float = 1.0
    remarks: Optional[str] = None

class ExaminationMarkResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    test_type: str
    test_date: date
    score: float
    max_score: float
    weight: float
    remarks: Optional[str]
    entered_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    student_name: Optional[str] = None
    subject_name: Optional[str] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True

# Result Formula Models
class ResultFormulaCreate(BaseModel):
    name: str
    description: str
    formula: str
    is_active: bool = True

class ResultFormulaResponse(BaseModel):
    id: int
    name: str
    description: str
    formula: str
    is_active: bool
    created_by: int
    created_at: datetime
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True

# Authentication endpoints
@router.post("/auth/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/auth/login", response_model=LoginResponse)
def login_user(login: LoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    user = authenticate_user(db, login.username, login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@router.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/auth/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset email"""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = create_access_token(
        data={"sub": user.username, "type": "password_reset"},
        expires_delta=timedelta(hours=1)
    )
    
    # In a real application, you would send an email here
    # For now, we'll just return a success message
    # TODO: Implement email sending functionality
    
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/auth/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token"""
    try:
        # Verify token
        payload = verify_token(request.token)
        if not payload or payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Update password
        user.hashed_password = get_password_hash(request.new_password)
        db.commit()
        
        return {"message": "Password reset successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

# User management endpoints
@router.get("/users", response_model=List[UserResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only see their own profile unless they're admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return user

# Student management endpoints
@router.post("/students", response_model=StudentResponse)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Create a new student"""
    # Check if student ID already exists
    existing_student = db.query(Student).filter(Student.student_id == student.student_id).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    # Check if admission number already exists
    existing_admission = db.query(Student).filter(Student.admission_number == student.admission_number).first()
    if existing_admission:
        raise HTTPException(status_code=400, detail="Admission number already exists")
    
    # Check if prem number already exists
    existing_prem = db.query(Student).filter(Student.prem_number == student.prem_number).first()
    if existing_prem:
        raise HTTPException(status_code=400, detail="Prem number already exists")
    
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.get("/students", response_model=List[StudentResponse])
def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    class_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all students with optional filtering"""
    query = db.query(Student)
    if class_id:
        query = query.filter(Student.class_id == class_id)
    
    students = query.offset(skip).limit(limit).all()
    return students

@router.get("/students/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_update: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Update student information"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for field, value in student_update.dict().items():
        setattr(db_student, field, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student

@router.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a student (admin only)"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

# Teacher management endpoints
@router.post("/teachers", response_model=TeacherResponse)
def create_teacher(
    teacher: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new teacher (admin only)"""
    existing_teacher = db.query(Teacher).filter(Teacher.employee_id == teacher.employee_id).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    db_teacher = Teacher(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@router.get("/teachers", response_model=List[TeacherResponse])
def get_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all teachers"""
    teachers = db.query(Teacher).offset(skip).limit(limit).all()
    return teachers

@router.get("/teachers/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get teacher by ID"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.put("/teachers/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    teacher_update: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update teacher information"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    for field, value in teacher_update.dict().items():
        setattr(teacher, field, value)
    
    db.commit()
    db.refresh(teacher)
    return teacher

@router.delete("/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a teacher (admin only)"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    teacher.is_active = False
    db.commit()
    return {"message": "Teacher deleted successfully"}

# Non-Teaching Staff management endpoints
@router.post("/non-teaching-staff", response_model=NonTeachingStaffResponse)
def create_non_teaching_staff(
    staff: NonTeachingStaffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new non-teaching staff member (admin only)"""
    existing_staff = db.query(NonTeachingStaff).filter(NonTeachingStaff.employee_id == staff.employee_id).first()
    if existing_staff:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    db_staff = NonTeachingStaff(**staff.dict())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff

@router.get("/non-teaching-staff", response_model=List[NonTeachingStaffResponse])
def get_non_teaching_staff(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all non-teaching staff with optional filtering"""
    query = db.query(NonTeachingStaff).filter(NonTeachingStaff.is_active == True)
    if department:
        query = query.filter(NonTeachingStaff.department == department)
    return query.offset(skip).limit(limit).all()

@router.get("/non-teaching-staff/{staff_id}", response_model=NonTeachingStaffResponse)
def get_non_teaching_staff_by_id(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get non-teaching staff by ID"""
    staff = db.query(NonTeachingStaff).filter(NonTeachingStaff.id == staff_id).first()
    if staff is None:
        raise HTTPException(status_code=404, detail="Non-teaching staff not found")
    return staff

@router.put("/non-teaching-staff/{staff_id}", response_model=NonTeachingStaffResponse)
def update_non_teaching_staff(
    staff_id: int,
    staff_update: NonTeachingStaffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update non-teaching staff information"""
    staff = db.query(NonTeachingStaff).filter(NonTeachingStaff.id == staff_id).first()
    if staff is None:
        raise HTTPException(status_code=404, detail="Non-teaching staff not found")
    
    for field, value in staff_update.dict().items():
        setattr(staff, field, value)
    
    db.commit()
    db.refresh(staff)
    return staff

@router.delete("/non-teaching-staff/{staff_id}")
def delete_non_teaching_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a non-teaching staff member (admin only)"""
    staff = db.query(NonTeachingStaff).filter(NonTeachingStaff.id == staff_id).first()
    if staff is None:
        raise HTTPException(status_code=404, detail="Non-teaching staff not found")
    
    staff.is_active = False
    db.commit()
    return {"message": "Non-teaching staff deleted successfully"}

# Class management endpoints
@router.post("/classes", response_model=ClassResponse)
def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new class (admin only)"""
    existing_class = db.query(Class).filter(Class.name == class_data.name).first()
    if existing_class:
        raise HTTPException(status_code=400, detail="Class name already exists")
    
    db_class = Class(**class_data.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@router.get("/classes", response_model=List[ClassResponse])
def get_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all classes"""
    classes = db.query(Class).offset(skip).limit(limit).all()
    return classes

@router.get("/classes/{class_id}", response_model=ClassResponse)
def get_class_by_id(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get class by ID"""
    class_info = db.query(Class).filter(Class.id == class_id).first()
    if class_info is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_info

@router.put("/classes/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    class_update: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update class information"""
    class_info = db.query(Class).filter(Class.id == class_id).first()
    if class_info is None:
        raise HTTPException(status_code=404, detail="Class not found")
    
    for field, value in class_update.dict().items():
        setattr(class_info, field, value)
    
    db.commit()
    db.refresh(class_info)
    return class_info

@router.delete("/classes/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a class (admin only)"""
    class_info = db.query(Class).filter(Class.id == class_id).first()
    if class_info is None:
        raise HTTPException(status_code=404, detail="Class not found")
    
    class_info.is_active = False
    db.commit()
    return {"message": "Class deleted successfully"}

# Subject management endpoints
@router.post("/subjects", response_model=dict)
def create_subject(
    subject_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new subject (admin only)"""
    existing_subject = db.query(Subject).filter(Subject.name == subject_data["name"]).first()
    if existing_subject:
        raise HTTPException(status_code=400, detail="Subject name already exists")
    
    db_subject = Subject(**subject_data)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return {"message": "Subject created successfully", "id": db_subject.id}

@router.get("/subjects", response_model=List[dict])
def get_subjects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all subjects"""
    subjects = db.query(Subject).offset(skip).limit(limit).all()
    return [{"id": s.id, "name": s.name, "code": s.code, "description": s.description, "credits": s.credits} for s in subjects]

@router.delete("/subjects/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a subject (admin only)"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(subject)
    db.commit()
    return {"message": "Subject deleted successfully"}

# Grade management endpoints
@router.post("/grades", response_model=GradeResponse)
def create_grade(
    grade: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Create a new grade"""
    # Calculate grade letter
    if grade.score >= 90:
        grade_letter = "A"
    elif grade.score >= 80:
        grade_letter = "B"
    elif grade.score >= 70:
        grade_letter = "C"
    elif grade.score >= 60:
        grade_letter = "D"
    else:
        grade_letter = "F"
    
    db_grade = Grade(
        student_id=grade.student_id,
        subject_id=grade.subject_id,
        score=grade.score,
        grade_letter=grade_letter,
        semester=grade.semester,
        academic_year=grade.academic_year
    )
    
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade

@router.get("/grades", response_model=List[GradeResponse])
def get_grades(
    student_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get grades with optional filtering"""
    query = db.query(Grade)
    if student_id:
        query = query.filter(Grade.student_id == student_id)
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    
    grades = query.offset(skip).limit(limit).all()
    return grades

@router.delete("/grades/{grade_id}")
def delete_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Delete a grade (teacher or admin only)"""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if grade is None:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    db.delete(grade)
    db.commit()
    return {"message": "Grade deleted successfully"}

# Attendance management endpoints
@router.post("/attendance", response_model=AttendanceResponse)
def mark_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Mark student attendance"""
    db_attendance = Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.get("/attendance", response_model=List[AttendanceResponse])
def get_attendance(
    student_id: Optional[int] = Query(None),
    class_id: Optional[int] = Query(None),
    date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get attendance records with optional filtering"""
    query = db.query(Attendance)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    if class_id:
        query = query.filter(Attendance.class_id == class_id)
    if date:
        query = query.filter(Attendance.date == date)
    
    attendance_records = query.offset(skip).limit(limit).all()
    return attendance_records

@router.delete("/attendance/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Delete an attendance record (teacher or admin only)"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    db.delete(attendance)
    db.commit()
    return {"message": "Attendance record deleted successfully"}

# Fee management endpoints
@router.post("/fees", response_model=dict)
def create_fee(
    fee_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new fee (admin only)"""
    db_fee = Fee(**fee_data)
    db.add(db_fee)
    db.commit()
    db.refresh(db_fee)
    return {"message": "Fee created successfully", "id": db_fee.id}

@router.get("/fees", response_model=List[dict])
def get_fees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all fees"""
    fees = db.query(Fee).filter(Fee.is_active == True).offset(skip).limit(limit).all()
    return [{"id": f.id, "name": f.name, "amount": f.amount, "description": f.description, "academic_year": f.academic_year, "due_date": f.due_date} for f in fees]

@router.delete("/fees/{fee_id}")
def delete_fee(
    fee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a fee (admin only)"""
    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    if fee is None:
        raise HTTPException(status_code=404, detail="Fee not found")
    
    fee.is_active = False
    db.commit()
    return {"message": "Fee deleted successfully"}

# Payment management endpoints
@router.post("/payments", response_model=dict)
def create_payment(
    payment_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Create a new payment"""
    db_payment = Payment(**payment_data)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return {"message": "Payment created successfully", "id": db_payment.id}

@router.get("/payments", response_model=List[dict])
def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all payments with optional filtering"""
    query = db.query(Payment)
    if student_id:
        query = query.filter(Payment.student_id == student_id)
    payments = query.offset(skip).limit(limit).all()
    return [{"id": p.id, "student_id": p.student_id, "fee_id": p.fee_id, "amount_paid": p.amount_paid, "payment_date": p.payment_date, "payment_method": p.payment_method, "receipt_number": p.receipt_number} for p in payments]

@router.delete("/payments/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a payment (admin only)"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    db.delete(payment)
    db.commit()
    return {"message": "Payment deleted successfully"}

# Event management endpoints
@router.post("/events", response_model=dict)
def create_event(
    event_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new event (admin only)"""
    db_event = Event(**event_data)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return {"message": "Event created successfully", "id": db_event.id}

@router.get("/events", response_model=List[dict])
def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all events with optional filtering"""
    query = db.query(Event).filter(Event.is_active == True)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    events = query.offset(skip).limit(limit).all()
    return [{"id": e.id, "title": e.title, "description": e.description, "start_date": e.start_date, "end_date": e.end_date, "location": e.location, "event_type": e.event_type} for e in events]

@router.delete("/events/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete an event (admin only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.is_active = False
    db.commit()
    return {"message": "Event deleted successfully"}

# Alumni endpoints
@router.post("/alumni", response_model=AlumniResponse)
def create_alumni(
    alumni: AlumniCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    db_alumni = Alumni(**alumni.dict())
    db.add(db_alumni)
    db.commit()
    db.refresh(db_alumni)
    return db_alumni

@router.get("/alumni", response_model=List[AlumniResponse])
def get_alumni(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    graduation_year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Alumni).filter(Alumni.is_active == True)
    if graduation_year:
        query = query.filter(Alumni.graduation_year == graduation_year)
    return query.offset(skip).limit(limit).all()

@router.get("/alumni/{alumni_id}", response_model=AlumniResponse)
def get_alumni_by_id(
    alumni_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    alumni = db.query(Alumni).filter(Alumni.id == alumni_id).first()
    if not alumni:
        raise HTTPException(status_code=404, detail="Alumni not found")
    return alumni

@router.put("/alumni/{alumni_id}", response_model=AlumniResponse)
def update_alumni(
    alumni_id: int,
    alumni_update: AlumniCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    alumni = db.query(Alumni).filter(Alumni.id == alumni_id).first()
    if not alumni:
        raise HTTPException(status_code=404, detail="Alumni not found")
    
    for key, value in alumni_update.dict().items():
        setattr(alumni, key, value)
    
    db.commit()
    db.refresh(alumni)
    return alumni

@router.delete("/alumni/{alumni_id}")
def delete_alumni(
    alumni_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    alumni = db.query(Alumni).filter(Alumni.id == alumni_id).first()
    if not alumni:
        raise HTTPException(status_code=404, detail="Alumni not found")
    
    alumni.is_active = False
    db.commit()
    return {"message": "Alumni deleted successfully"}

# Donor endpoints
@router.post("/donors", response_model=DonorResponse)
def create_donor(
    donor: DonorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_donor = Donor(**donor.dict())
    db.add(db_donor)
    db.commit()
    db.refresh(db_donor)
    return db_donor

@router.get("/donors", response_model=List[DonorResponse])
def get_donors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    donor_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Donor).filter(Donor.is_active == True)
    if donor_type:
        query = query.filter(Donor.donor_type == donor_type)
    return query.offset(skip).limit(limit).all()

@router.get("/donors/{donor_id}", response_model=DonorResponse)
def get_donor_by_id(
    donor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    return donor

@router.put("/donors/{donor_id}", response_model=DonorResponse)
def update_donor(
    donor_id: int,
    donor_update: DonorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    for key, value in donor_update.dict().items():
        setattr(donor, key, value)
    
    db.commit()
    db.refresh(donor)
    return donor

@router.delete("/donors/{donor_id}")
def delete_donor(
    donor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    donor.is_active = False
    db.commit()
    return {"message": "Donor deleted successfully"}

# Donation endpoints
@router.post("/donations", response_model=DonationResponse)
def create_donation(
    donation: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Verify donor exists
    donor = db.query(Donor).filter(Donor.id == donation.donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    db_donation = Donation(**donation.dict())
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)
    return db_donation

@router.get("/donations", response_model=List[DonationResponse])
def get_donations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    donor_id: Optional[int] = Query(None),
    purpose: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Donation).join(Donor)
    if donor_id:
        query = query.filter(Donation.donor_id == donor_id)
    if purpose:
        query = query.filter(Donation.purpose == purpose)
    return query.offset(skip).limit(limit).all()

@router.get("/donations/{donation_id}", response_model=DonationResponse)
def get_donation_by_id(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    return donation

# File upload endpoints
@router.post("/upload/passport-photo")
async def upload_passport_photo(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload passport size photo for a user"""
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/passport_photos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"passport_photo_{user_id}_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user record
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.passport_photo = file_path
    db.commit()
    
    return {"message": "Passport photo uploaded successfully", "file_path": file_path}

@router.post("/upload/seminary-logo")
async def upload_seminary_logo(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload seminary logo for a user"""
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/seminary_logos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"seminary_logo_{user_id}_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user record
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.seminary_logo = file_path
    db.commit()
    
    return {"message": "Seminary logo uploaded successfully", "file_path": file_path}

# Subject Teacher endpoints
@router.post("/subject-teachers", response_model=SubjectTeacherResponse)
def create_subject_teacher(
    subject_teacher: SubjectTeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Create a new subject teacher assignment"""
    # Verify subject and teacher exist
    subject = db.query(Subject).filter(Subject.id == subject_teacher.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    teacher = db.query(Teacher).filter(Teacher.id == subject_teacher.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Check if assignment already exists
    existing = db.query(SubjectTeacher).filter(
        SubjectTeacher.subject_id == subject_teacher.subject_id,
        SubjectTeacher.teacher_id == subject_teacher.teacher_id,
        SubjectTeacher.academic_year == subject_teacher.academic_year
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Subject teacher assignment already exists")
    
    db_subject_teacher = SubjectTeacher(**subject_teacher.dict())
    db.add(db_subject_teacher)
    db.commit()
    db.refresh(db_subject_teacher)
    
    # Add subject and teacher names for response
    response = SubjectTeacherResponse.from_orm(db_subject_teacher)
    response.subject_name = subject.name
    response.teacher_name = teacher.user.full_name
    
    return response

@router.get("/subject-teachers", response_model=List[SubjectTeacherResponse])
def get_subject_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    subject_id: Optional[int] = Query(None),
    teacher_id: Optional[int] = Query(None),
    academic_year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get subject teacher assignments"""
    query = db.query(SubjectTeacher)
    
    if subject_id:
        query = query.filter(SubjectTeacher.subject_id == subject_id)
    if teacher_id:
        query = query.filter(SubjectTeacher.teacher_id == teacher_id)
    if academic_year:
        query = query.filter(SubjectTeacher.academic_year == academic_year)
    
    subject_teachers = query.offset(skip).limit(limit).all()
    
    # Add subject and teacher names
    result = []
    for st in subject_teachers:
        response = SubjectTeacherResponse.from_orm(st)
        response.subject_name = st.subject.name
        response.teacher_name = st.teacher.user.full_name
        result.append(response)
    
    return result

# Student Result endpoints
@router.post("/student-results", response_model=StudentResultResponse)
def create_student_result(
    result: StudentResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Create a new student result"""
    # Verify student exists
    student = db.query(Student).filter(Student.id == result.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if result already exists for this student, term, and academic year
    existing = db.query(StudentResult).filter(
        StudentResult.student_id == result.student_id,
        StudentResult.term == result.term,
        StudentResult.academic_year == result.academic_year
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Result already exists for this student, term, and academic year")
    
    # Create the main result record
    db_result = StudentResult(
        student_id=result.student_id,
        academic_year=result.academic_year,
        term=result.term,
        total_subjects=result.total_subjects,
        total_score=result.total_score,
        average_score=result.average_score,
        position_in_class=result.position_in_class,
        total_students_in_class=result.total_students_in_class,
        remarks=result.remarks,
        date_issued=result.date_issued,
        issued_by=current_user.id
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    # Create result details
    for detail in result.result_details:
        db_detail = StudentResultDetail(
            result_id=db_result.id,
            subject_id=detail.subject_id,
            subject_teacher_id=detail.subject_teacher_id,
            score=detail.score,
            grade_letter=detail.grade_letter,
            remarks=detail.remarks
        )
        db.add(db_detail)
    
    db.commit()
    
    # Return the complete result with details
    return get_student_result_by_id(db_result.id, db, current_user)

@router.get("/student-results", response_model=List[StudentResultResponse])
def get_student_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: Optional[int] = Query(None),
    academic_year: Optional[str] = Query(None),
    term: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get student results"""
    query = db.query(StudentResult)
    
    if student_id:
        query = query.filter(StudentResult.student_id == student_id)
    if academic_year:
        query = query.filter(StudentResult.academic_year == academic_year)
    if term:
        query = query.filter(StudentResult.term == term)
    
    results = query.offset(skip).limit(limit).all()
    
    # Add student and class names, and result details
    result_list = []
    for result in results:
        response = StudentResultResponse.from_orm(result)
        response.student_name = result.student.full_name
        response.class_name = result.student.class_info.name if result.student.class_info else None
        
        # Get result details
        details = db.query(StudentResultDetail).filter(
            StudentResultDetail.result_id == result.id
        ).all()
        
        detail_responses = []
        for detail in details:
            detail_response = StudentResultDetailResponse.from_orm(detail)
            detail_response.subject_name = detail.subject.name
            detail_response.teacher_name = detail.subject_teacher.teacher.user.full_name
            detail_responses.append(detail_response)
        
        response.result_details = detail_responses
        result_list.append(response)
    
    return result_list

@router.get("/student-results/{result_id}", response_model=StudentResultResponse)
def get_student_result_by_id(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific student result by ID"""
    result = db.query(StudentResult).filter(StudentResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Student result not found")
    
    response = StudentResultResponse.from_orm(result)
    response.student_name = result.student.full_name
    response.class_name = result.student.class_info.name if result.student.class_info else None
    
    # Get result details
    details = db.query(StudentResultDetail).filter(
        StudentResultDetail.result_id == result.id
    ).all()
    
    detail_responses = []
    for detail in details:
        detail_response = StudentResultDetailResponse.from_orm(detail)
        detail_response.subject_name = detail.subject.name
        detail_response.teacher_name = detail.subject_teacher.teacher.user.full_name
        detail_responses.append(detail_response)
    
    response.result_details = detail_responses
    return response

@router.delete("/student-results/{result_id}")
def delete_student_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Delete a student result"""
    result = db.query(StudentResult).filter(StudentResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Student result not found")
    
    # Delete result details first
    db.query(StudentResultDetail).filter(StudentResultDetail.result_id == result_id).delete()
    
    # Delete the main result
    db.delete(result)
    db.commit()
    
    return {"message": "Student result deleted successfully"}

# Teacher Assignment endpoints
@router.post("/teacher-assignments", response_model=TeacherAssignmentResponse)
def create_teacher_assignment(
    assignment: TeacherAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Create a new teacher assignment"""
    # Verify teacher, subject, and class exist
    teacher = db.query(Teacher).filter(Teacher.id == assignment.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    subject = db.query(Subject).filter(Subject.id == assignment.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    class_info = db.query(Class).filter(Class.id == assignment.class_id).first()
    if not class_info:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check if assignment already exists
    existing_assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == assignment.teacher_id,
        TeacherAssignment.subject_id == assignment.subject_id,
        TeacherAssignment.class_id == assignment.class_id,
        TeacherAssignment.academic_year == assignment.academic_year,
        TeacherAssignment.term == assignment.term
    ).first()
    
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Assignment already exists")
    
    db_assignment = TeacherAssignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    # Add names to response
    response = TeacherAssignmentResponse.from_orm(db_assignment)
    response.teacher_name = teacher.user.full_name
    response.subject_name = subject.name
    response.class_name = class_info.name
    
    return response

@router.get("/teacher-assignments", response_model=List[TeacherAssignmentResponse])
def get_teacher_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    teacher_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    class_id: Optional[int] = Query(None),
    academic_year: Optional[str] = Query(None),
    term: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get teacher assignments"""
    query = db.query(TeacherAssignment)
    
    if teacher_id:
        query = query.filter(TeacherAssignment.teacher_id == teacher_id)
    if subject_id:
        query = query.filter(TeacherAssignment.subject_id == subject_id)
    if class_id:
        query = query.filter(TeacherAssignment.class_id == class_id)
    if academic_year:
        query = query.filter(TeacherAssignment.academic_year == academic_year)
    if term:
        query = query.filter(TeacherAssignment.term == term)
    
    assignments = query.offset(skip).limit(limit).all()
    
    # Add names to responses
    assignment_list = []
    for assignment in assignments:
        response = TeacherAssignmentResponse.from_orm(assignment)
        response.teacher_name = assignment.teacher.user.full_name
        response.subject_name = assignment.subject.name
        response.class_name = assignment.class_info.name
        assignment_list.append(response)
    
    return assignment_list

@router.get("/teacher-assignments/{assignment_id}", response_model=TeacherAssignmentResponse)
def get_teacher_assignment_by_id(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific teacher assignment by ID"""
    assignment = db.query(TeacherAssignment).filter(TeacherAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Teacher assignment not found")
    
    response = TeacherAssignmentResponse.from_orm(assignment)
    response.teacher_name = assignment.teacher.user.full_name
    response.subject_name = assignment.subject.name
    response.class_name = assignment.class_info.name
    
    return response

@router.delete("/teacher-assignments/{assignment_id}")
def delete_teacher_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Delete a teacher assignment"""
    assignment = db.query(TeacherAssignment).filter(TeacherAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Teacher assignment not found")
    
    db.delete(assignment)
    db.commit()
    
    return {"message": "Teacher assignment deleted successfully"}

# Examination Mark endpoints
@router.post("/examination-marks", response_model=ExaminationMarkResponse)
def create_examination_mark(
    mark: ExaminationMarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Create a new examination mark"""
    # Verify assignment and student exist
    assignment = db.query(TeacherAssignment).filter(TeacherAssignment.id == mark.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Teacher assignment not found")
    
    student = db.query(Student).filter(Student.id == mark.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if mark already exists for this student, assignment, and test type
    existing_mark = db.query(ExaminationMark).filter(
        ExaminationMark.assignment_id == mark.assignment_id,
        ExaminationMark.student_id == mark.student_id,
        ExaminationMark.test_type == mark.test_type,
        ExaminationMark.test_date == mark.test_date
    ).first()
    
    if existing_mark:
        raise HTTPException(status_code=400, detail="Mark already exists for this test")
    
    db_mark = ExaminationMark(**mark.dict(), entered_by=current_user.id)
    db.add(db_mark)
    db.commit()
    db.refresh(db_mark)
    
    # Add names to response
    response = ExaminationMarkResponse.from_orm(db_mark)
    response.student_name = student.full_name
    response.subject_name = assignment.subject.name
    response.teacher_name = assignment.teacher.user.full_name
    
    return response

@router.get("/examination-marks", response_model=List[ExaminationMarkResponse])
def get_examination_marks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    assignment_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    test_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get examination marks"""
    query = db.query(ExaminationMark)
    
    if assignment_id:
        query = query.filter(ExaminationMark.assignment_id == assignment_id)
    if student_id:
        query = query.filter(ExaminationMark.student_id == student_id)
    if test_type:
        query = query.filter(ExaminationMark.test_type == test_type)
    
    marks = query.offset(skip).limit(limit).all()
    
    # Add names to responses
    mark_list = []
    for mark in marks:
        response = ExaminationMarkResponse.from_orm(mark)
        response.student_name = mark.student.full_name
        response.subject_name = mark.assignment.subject.name
        response.teacher_name = mark.assignment.teacher.user.full_name
        mark_list.append(response)
    
    return mark_list

@router.put("/examination-marks/{mark_id}", response_model=ExaminationMarkResponse)
def update_examination_mark(
    mark_id: int,
    mark_update: ExaminationMarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Update an examination mark"""
    mark = db.query(ExaminationMark).filter(ExaminationMark.id == mark_id).first()
    if not mark:
        raise HTTPException(status_code=404, detail="Examination mark not found")
    
    # Update mark data
    for field, value in mark_update.dict().items():
        setattr(mark, field, value)
    
    db.commit()
    db.refresh(mark)
    
    # Add names to response
    response = ExaminationMarkResponse.from_orm(mark)
    response.student_name = mark.student.full_name
    response.subject_name = mark.assignment.subject.name
    response.teacher_name = mark.assignment.teacher.user.full_name
    
    return response

@router.delete("/examination-marks/{mark_id}")
def delete_examination_mark(
    mark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Delete an examination mark"""
    mark = db.query(ExaminationMark).filter(ExaminationMark.id == mark_id).first()
    if not mark:
        raise HTTPException(status_code=404, detail="Examination mark not found")
    
    db.delete(mark)
    db.commit()
    
    return {"message": "Examination mark deleted successfully"}

# Result Formula endpoints
@router.post("/result-formulas", response_model=ResultFormulaResponse)
def create_result_formula(
    formula: ResultFormulaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new result formula"""
    # Check if formula name already exists
    existing_formula = db.query(ResultFormula).filter(ResultFormula.name == formula.name).first()
    if existing_formula:
        raise HTTPException(status_code=400, detail="Formula name already exists")
    
    db_formula = ResultFormula(**formula.dict(), created_by=current_user.id)
    db.add(db_formula)
    db.commit()
    db.refresh(db_formula)
    
    # Add creator name to response
    response = ResultFormulaResponse.from_orm(db_formula)
    response.created_by_name = current_user.full_name
    
    return response

@router.get("/result-formulas", response_model=List[ResultFormulaResponse])
def get_result_formulas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get result formulas"""
    query = db.query(ResultFormula)
    
    if is_active is not None:
        query = query.filter(ResultFormula.is_active == is_active)
    
    formulas = query.offset(skip).limit(limit).all()
    
    # Add creator names to responses
    formula_list = []
    for formula in formulas:
        response = ResultFormulaResponse.from_orm(formula)
        response.created_by_name = formula.created_by_user.full_name
        formula_list.append(response)
    
    return formula_list

@router.get("/result-formulas/{formula_id}", response_model=ResultFormulaResponse)
def get_result_formula_by_id(
    formula_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific result formula by ID"""
    formula = db.query(ResultFormula).filter(ResultFormula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="Result formula not found")
    
    response = ResultFormulaResponse.from_orm(formula)
    response.created_by_name = formula.created_by_user.full_name
    
    return response

@router.put("/result-formulas/{formula_id}", response_model=ResultFormulaResponse)
def update_result_formula(
    formula_id: int,
    formula_update: ResultFormulaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a result formula"""
    formula = db.query(ResultFormula).filter(ResultFormula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="Result formula not found")
    
    # Check if new name conflicts with existing formula
    if formula_update.name != formula.name:
        existing_formula = db.query(ResultFormula).filter(ResultFormula.name == formula_update.name).first()
        if existing_formula:
            raise HTTPException(status_code=400, detail="Formula name already exists")
    
    # Update formula data
    for field, value in formula_update.dict().items():
        setattr(formula, field, value)
    
    db.commit()
    db.refresh(formula)
    
    # Add creator name to response
    response = ResultFormulaResponse.from_orm(formula)
    response.created_by_name = formula.created_by_user.full_name
    
    return response

@router.delete("/result-formulas/{formula_id}")
def delete_result_formula(
    formula_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a result formula"""
    formula = db.query(ResultFormula).filter(ResultFormula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="Result formula not found")
    
    db.delete(formula)
    db.commit()
    
    return {"message": "Result formula deleted successfully"}

# Health check endpoint
@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running", "timestamp": datetime.utcnow()}

# Include monitoring routes
# router.include_router(monitoring_router)

# Include file management routes
# router.include_router(file_router)

# Include email management routes
# router.include_router(email_router)

# Include report management routes
# router.include_router(report_router)

# Include calendar management routes
# router.include_router(calendar_router)

# Include search management routes
# router.include_router(search_router)

# Include data export routes
# router.include_router(export_router) 