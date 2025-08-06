from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ADMINISTRATOR = "administrator"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    NON_TEACHING_STAFF = "non_teaching_staff"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.STUDENT)
    passport_photo = Column(String, nullable=True)  # Path to passport size photo
    seminary_logo = Column(String, nullable=True)   # Path to seminary logo
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False)
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)
    non_teaching_staff_profile = relationship("NonTeachingStaff", back_populates="user", uselist=False)
    attendance_records = relationship("Attendance", back_populates="user", foreign_keys="Attendance.user_id")
    # Phase 4 relationships (commented out for now)
    # uploaded_files = relationship("FileRecord", back_populates="uploader")
    # sent_emails = relationship("EmailLog", back_populates="sender")
    # calendar_events = relationship("CalendarEvent", back_populates="creator")
    # event_participants = relationship("EventParticipant", back_populates="user")

class Alumni(Base):
    __tablename__ = "alumni"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String)
    phone = Column(String)
    graduation_year = Column(Integer)
    class_name = Column(String)  # Store the class name at graduation
    current_occupation = Column(String, nullable=True)
    employer = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    achievements = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Donor(Base):
    __tablename__ = "donors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    donor_type = Column(String)  # individual, corporate, foundation, etc.
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    donations = relationship("Donation", back_populates="donor")

class Donation(Base):
    __tablename__ = "donations"
    
    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("donors.id"))
    amount = Column(Float)
    donation_date = Column(Date)
    purpose = Column(String, nullable=True)  # scholarship, building, equipment, etc.
    payment_method = Column(String, nullable=True)
    receipt_number = Column(String, unique=True, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    donor = relationship("Donor", back_populates="donations")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    student_id = Column(String, unique=True, index=True)
    admission_number = Column(String, unique=True, index=True)  # Admission number
    prem_number = Column(String, unique=True, index=True)  # Prem number
    full_name = Column(String)  # Add full_name field for easier access
    date_of_birth = Column(Date)
    gender = Column(String)
    address = Column(Text)
    phone = Column(String)
    parent_name = Column(String)
    parent_phone = Column(String)
    admission_date = Column(Date)
    class_id = Column(Integer, ForeignKey("classes.id"))
    student_level = Column(String)  # "O-Level" or "A-Level"
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    class_info = relationship("Class", back_populates="students")
    grades = relationship("Grade", back_populates="student")
    payments = relationship("Payment", back_populates="student")
    results = relationship("StudentResult", back_populates="student")

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    employee_id = Column(String, unique=True, index=True)
    department = Column(String)
    qualification = Column(String)
    hire_date = Column(Date)
    phone = Column(String)
    address = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    classes = relationship("Class", back_populates="teacher")
    subject_assignments = relationship("SubjectTeacher", back_populates="teacher")

class NonTeachingStaff(Base):
    __tablename__ = "non_teaching_staff"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    employee_id = Column(String, unique=True, index=True)
    department = Column(String)  # admin, maintenance, security, kitchen, etc.
    position = Column(String)  # secretary, accountant, cleaner, etc.
    hire_date = Column(Date)
    phone = Column(String)
    address = Column(Text)
    salary = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="non_teaching_staff_profile")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    capacity = Column(Integer)
    academic_year = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="classes")
    students = relationship("Student", back_populates="class_info")
    subjects = relationship("ClassSubject", back_populates="class_info")

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    code = Column(String, unique=True)
    description = Column(Text)
    credits = Column(Integer)
    subject_level = Column(String)  # "O-Level" or "A-Level"
    
    # Relationships
    class_subjects = relationship("ClassSubject", back_populates="subject")
    subject_teachers = relationship("SubjectTeacher", back_populates="subject")

class SubjectTeacher(Base):
    __tablename__ = "subject_teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    academic_year = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subject = relationship("Subject", back_populates="subject_teachers")
    teacher = relationship("Teacher", back_populates="subject_assignments")

class ClassSubject(Base):
    __tablename__ = "class_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    # Relationships
    class_info = relationship("Class", back_populates="subjects")
    subject = relationship("Subject", back_populates="class_subjects")
    grades = relationship("Grade", back_populates="class_subject")

class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    class_subject_id = Column(Integer, ForeignKey("class_subjects.id"))
    score = Column(Float)
    grade_letter = Column(String)
    semester = Column(String)
    academic_year = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="grades")
    class_subject = relationship("ClassSubject", back_populates="grades")

class StudentResult(Base):
    __tablename__ = "student_results"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    academic_year = Column(String)
    term = Column(String)  # First Term, Second Term, Third Term, Final
    total_subjects = Column(Integer)
    total_score = Column(Float)
    average_score = Column(Float)
    position_in_class = Column(Integer, nullable=True)
    total_students_in_class = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)
    date_issued = Column(Date)
    issued_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="results")
    result_details = relationship("StudentResultDetail", back_populates="result")
    issued_by_user = relationship("User")

class StudentResultDetail(Base):
    __tablename__ = "student_result_details"
    
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("student_results.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    subject_teacher_id = Column(Integer, ForeignKey("subject_teachers.id"))
    score = Column(Float)
    grade_letter = Column(String)
    remarks = Column(Text, nullable=True)
    
    # Relationships
    result = relationship("StudentResult", back_populates="result_details")
    subject = relationship("Subject")
    subject_teacher = relationship("SubjectTeacher")

class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    academic_year = Column(String)
    term = Column(String)  # First Term, Second Term, Third Term, Final
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    teacher = relationship("Teacher")
    subject = relationship("Subject")
    class_info = relationship("Class")
    examination_marks = relationship("ExaminationMark", back_populates="assignment")

class ExaminationMark(Base):
    __tablename__ = "examination_marks"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("teacher_assignments.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    test_type = Column(String)  # Mid-term, End-term, Final, Assignment, etc.
    test_date = Column(Date)
    score = Column(Float)
    max_score = Column(Float, default=100.0)
    weight = Column(Float, default=1.0)  # Weight for formula calculation
    remarks = Column(Text, nullable=True)
    entered_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assignment = relationship("TeacherAssignment", back_populates="examination_marks")
    student = relationship("Student")
    entered_by_user = relationship("User")

class ResultFormula(Base):
    __tablename__ = "result_formulas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)
    formula = Column(Text)  # JSON string containing formula logic
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    created_by_user = relationship("User")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    date = Column(Date)
    is_present = Column(Boolean, default=True)
    reason = Column(String, nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="attendance_records", foreign_keys=[user_id])
    recorded_by_user = relationship("User", foreign_keys=[recorded_by])

class Fee(Base):
    __tablename__ = "fees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    amount = Column(Float)
    description = Column(Text)
    academic_year = Column(String)
    is_active = Column(Boolean, default=True)
    due_date = Column(Date)
    
    # Relationships
    payments = relationship("Payment", back_populates="fee")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    fee_id = Column(Integer, ForeignKey("fees.id"))
    amount_paid = Column(Float)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    payment_method = Column(String)
    receipt_number = Column(String, unique=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="payments")
    fee = relationship("Fee", back_populates="payments")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    location = Column(String)
    event_type = Column(String)  # academic, social, religious, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 