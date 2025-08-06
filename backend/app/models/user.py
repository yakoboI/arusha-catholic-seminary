"""
User Model
Clean user model for Arusha Catholic Seminary
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    ADMINISTRATOR = "administrator"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    NON_TEACHING_STAFF = "non_teaching_staff"


class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile fields
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default=UserRole.STUDENT, nullable=False)
    
    # Profile images
    passport_photo = Column(String(255), nullable=True)
    seminary_logo = Column(String(255), nullable=True)
    
    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Additional fields
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(10), nullable=True)
    
    # Relationships - using polymorphic approach
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role in [UserRole.ADMIN, UserRole.ADMINISTRATOR]
    
    @property
    def is_teacher(self) -> bool:
        """Check if user is teacher"""
        return self.role == UserRole.TEACHER
    
    @property
    def is_student(self) -> bool:
        """Check if user is student"""
        return self.role == UserRole.STUDENT
    
    @property
    def is_parent(self) -> bool:
        """Check if user is parent"""
        return self.role == UserRole.PARENT
    
    @property
    def is_staff(self) -> bool:
        """Check if user is staff"""
        return self.role == UserRole.NON_TEACHING_STAFF
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        # Admin has all permissions
        if self.is_admin:
            return True
        
        # Define permission mappings
        permission_map = {
            "read_students": [UserRole.TEACHER, UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "write_students": [UserRole.TEACHER, UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "read_teachers": [UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "write_teachers": [UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "read_grades": [UserRole.TEACHER, UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "write_grades": [UserRole.TEACHER, UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "read_attendance": [UserRole.TEACHER, UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "write_attendance": [UserRole.TEACHER, UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "read_reports": [UserRole.TEACHER, UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "write_reports": [UserRole.TEACHER, UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "manage_users": [UserRole.ADMIN, UserRole.ADMINISTRATOR],
            "manage_system": [UserRole.ADMIN, UserRole.ADMINISTRATOR],
        }
        
        return self.role in permission_map.get(permission, [])


class UserProfile(Base):
    """Polymorphic user profile model"""
    
    __tablename__ = "user_profiles"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to user
    user_id = Column(Integer, nullable=False, index=True)
    
    # Profile type
    profile_type = Column(String(20), nullable=False, index=True)
    
    # Common profile fields
    employee_id = Column(String(50), nullable=True, index=True)
    student_id = Column(String(50), nullable=True, index=True)
    admission_number = Column(String(50), nullable=True, index=True)
    prem_number = Column(String(50), nullable=True, index=True)
    
    # Academic fields
    class_id = Column(Integer, nullable=True)
    department = Column(String(100), nullable=True)
    qualification = Column(String(100), nullable=True)
    student_level = Column(String(20), nullable=True)  # O-Level, A-Level
    
    # Employment fields
    position = Column(String(100), nullable=True)
    hire_date = Column(DateTime, nullable=True)
    salary = Column(Integer, nullable=True)
    
    # Academic fields
    graduation_year = Column(Integer, nullable=True)
    class_name = Column(String(50), nullable=True)
    
    # Professional fields
    current_occupation = Column(String(100), nullable=True)
    employer = Column(String(100), nullable=True)
    achievements = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, type='{self.profile_type}')>"
    
    @property
    def is_student_profile(self) -> bool:
        """Check if this is a student profile"""
        return self.profile_type == "student"
    
    @property
    def is_teacher_profile(self) -> bool:
        """Check if this is a teacher profile"""
        return self.profile_type == "teacher"
    
    @property
    def is_staff_profile(self) -> bool:
        """Check if this is a staff profile"""
        return self.profile_type == "staff"
    
    @property
    def is_alumni_profile(self) -> bool:
        """Check if this is an alumni profile"""
        return self.profile_type == "alumni"


class PasswordReset(Base):
    """Password reset token model"""
    
    __tablename__ = "password_resets"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to user
    user_id = Column(Integer, nullable=False, index=True)
    
    # Token fields
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<PasswordReset(id={self.id}, user_id={self.user_id}, is_used={self.is_used})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at


class UserSession(Base):
    """User session model for tracking active sessions"""
    
    __tablename__ = "user_sessions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to user
    user_id = Column(Integer, nullable=False, index=True)
    
    # Session fields
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Device information
    device_info = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
