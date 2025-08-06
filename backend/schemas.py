#!/usr/bin/env python3
"""
Arusha Catholic Seminary - Pydantic Schemas
API request and response models
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date, datetime

# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None

# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    success: bool
    data: dict
    message: str

class RegisterResponse(BaseModel):
    success: bool
    data: dict
    message: str

class GenericResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str

# ============================================================================
# STUDENT SCHEMAS
# ============================================================================

class StudentBase(BaseModel):
    student_number: str = Field(..., min_length=1, max_length=20)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    gender: str = Field(..., pattern="^(Male|Female)$")
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    grade: str = Field(..., min_length=2, max_length=10)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(Male|Female)$")
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    grade: Optional[str] = Field(None, min_length=2, max_length=10)
    is_active: Optional[bool] = None

class StudentResponse(StudentBase):
    id: int
    enrollment_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# TEACHER SCHEMAS
# ============================================================================

class TeacherBase(BaseModel):
    employee_number: str = Field(..., min_length=1, max_length=20)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    gender: str = Field(..., pattern="^(Male|Female)$")
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    subject: str = Field(..., min_length=1, max_length=50)
    experience_years: int = Field(0, ge=0)
    qualification: Optional[str] = None

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(Male|Female)$")
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=50)
    experience_years: Optional[int] = Field(None, ge=0)
    qualification: Optional[str] = None
    is_active: Optional[bool] = None

class TeacherResponse(TeacherBase):
    id: int
    hire_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# CLASS SCHEMAS
# ============================================================================

class ClassBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)
    teacher_id: Optional[int] = None
    capacity: int = Field(30, ge=1, le=100)
    current_students: int = Field(0, ge=0)
    academic_year: str = Field(..., min_length=4, max_length=10)

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=20)
    teacher_id: Optional[int] = None
    capacity: Optional[int] = Field(None, ge=1, le=100)
    current_students: Optional[int] = Field(None, ge=0)
    academic_year: Optional[str] = Field(None, min_length=4, max_length=10)
    is_active: Optional[bool] = None

class ClassResponse(ClassBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# SUBJECT SCHEMAS
# ============================================================================

class SubjectBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    credits: int = Field(1, ge=1, le=10)

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    credits: Optional[int] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None

class SubjectResponse(SubjectBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# ATTENDANCE SCHEMAS
# ============================================================================

class AttendanceBase(BaseModel):
    student_id: int
    date: date
    status: str = Field(..., pattern="^(present|absent|late|excused)$")
    remarks: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(present|absent|late|excused)$")
    remarks: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# GRADE SCHEMAS
# ============================================================================

class GradeBase(BaseModel):
    student_id: int
    subject_id: int
    term: str = Field(..., min_length=1, max_length=20)
    academic_year: str = Field(..., min_length=4, max_length=10)
    score: float = Field(..., ge=0, le=100)
    max_score: float = Field(100.0, ge=1)
    grade_letter: Optional[str] = Field(None, pattern="^[A-F]$")
    remarks: Optional[str] = None

class GradeCreate(GradeBase):
    pass

class GradeUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    max_score: Optional[float] = Field(None, ge=1)
    grade_letter: Optional[str] = Field(None, pattern="^[A-F]$")
    remarks: Optional[str] = None

class GradeResponse(GradeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# NON-TEACHING STAFF SCHEMAS
# ============================================================================

class NonTeachingStaffBase(BaseModel):
    employee_number: str = Field(..., min_length=1, max_length=20)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    position: str = Field(..., min_length=1, max_length=100)
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class NonTeachingStaffCreate(NonTeachingStaffBase):
    pass

class NonTeachingStaffUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    position: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class NonTeachingStaffResponse(NonTeachingStaffBase):
    id: int
    hire_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# PARENT SCHEMAS
# ============================================================================

class ParentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    relationship: str = Field(..., pattern="^(Father|Mother|Guardian)$")
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    occupation: Optional[str] = None

class ParentCreate(ParentBase):
    pass

class ParentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    relationship: Optional[str] = Field(None, pattern="^(Father|Mother|Guardian)$")
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    occupation: Optional[str] = None
    is_active: Optional[bool] = None

class ParentResponse(ParentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# ALUMNI SCHEMAS
# ============================================================================

class AlumniBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    graduation_year: int = Field(..., ge=1900, le=2100)
    grade_at_graduation: Optional[str] = None
    current_occupation: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class AlumniCreate(AlumniBase):
    pass

class AlumniUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    graduation_year: Optional[int] = Field(None, ge=1900, le=2100)
    grade_at_graduation: Optional[str] = None
    current_occupation: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class AlumniResponse(AlumniBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# DONOR SCHEMAS
# ============================================================================

class DonorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(Individual|Organization|Corporate)$")
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    total_donations: float = Field(0.0, ge=0)
    last_donation_date: Optional[date] = None

class DonorCreate(DonorBase):
    pass

class DonorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, pattern="^(Individual|Organization|Corporate)$")
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    total_donations: Optional[float] = Field(None, ge=0)
    last_donation_date: Optional[date] = None
    is_active: Optional[bool] = None

class DonorResponse(DonorBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# LIST RESPONSE SCHEMAS
# ============================================================================

class StudentListResponse(BaseModel):
    success: bool
    data: List[StudentResponse]
    total: int
    message: str

class TeacherListResponse(BaseModel):
    success: bool
    data: List[TeacherResponse]
    total: int
    message: str

class ClassListResponse(BaseModel):
    success: bool
    data: List[ClassResponse]
    total: int
    message: str

class SubjectListResponse(BaseModel):
    success: bool
    data: List[SubjectResponse]
    total: int
    message: str

class AttendanceListResponse(BaseModel):
    success: bool
    data: List[AttendanceResponse]
    total: int
    message: str

class GradeListResponse(BaseModel):
    success: bool
    data: List[GradeResponse]
    total: int
    message: str

class NonTeachingStaffListResponse(BaseModel):
    success: bool
    data: List[NonTeachingStaffResponse]
    total: int
    message: str

class ParentListResponse(BaseModel):
    success: bool
    data: List[ParentResponse]
    total: int
    message: str

class AlumniListResponse(BaseModel):
    success: bool
    data: List[AlumniResponse]
    total: int
    message: str

class DonorListResponse(BaseModel):
    success: bool
    data: List[DonorResponse]
    total: int
    message: str
