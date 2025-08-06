"""
Report Management Models

This module defines the database models and Pydantic schemas for
report templates, generation logs, and scheduled reports.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from ..database import Base


class ReportType(str, Enum):
    """Report types"""
    STUDENT_LIST = "student_list"
    GRADE_REPORT = "grade_report"
    ATTENDANCE_REPORT = "attendance_report"
    FINANCIAL_REPORT = "financial_report"
    STAFF_REPORT = "staff_report"
    ALUMNI_REPORT = "alumni_report"
    DONATION_REPORT = "donation_report"
    EVENT_REPORT = "event_report"
    CUSTOM_REPORT = "custom_report"
    ANALYTICS_REPORT = "analytics_report"


class ReportFormat(str, Enum):
    """Report output formats"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    JSON = "json"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduleFrequency(str, Enum):
    """Report schedule frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ReportTemplate(Base):
    """Database model for report templates"""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False, index=True)
    template_config = Column(JSON, nullable=False)  # Template configuration
    query_config = Column(JSON, nullable=False)  # Database query configuration
    output_formats = Column(JSON, nullable=False)  # Supported output formats
    parameters = Column(JSON, nullable=True)  # Report parameters
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class ReportLog(Base):
    """Database model for report generation logs"""
    __tablename__ = "report_logs"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=True)
    report_name = Column(String(100), nullable=False)
    report_type = Column(String(50), nullable=False, index=True)
    output_format = Column(String(20), nullable=False)
    status = Column(String(20), default=ReportStatus.PENDING, nullable=False, index=True)
    file_path = Column(String(500), nullable=True)  # Generated file path
    file_size = Column(Integer, nullable=True)  # File size in bytes
    parameters = Column(JSON, nullable=True)  # Report parameters used
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)  # Processing time in seconds
    record_count = Column(Integer, nullable=True)  # Number of records processed
    generated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    template = relationship("ReportTemplate")
    creator = relationship("User")


class ReportSchedule(Base):
    """Database model for scheduled reports"""
    __tablename__ = "report_schedules"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(String(20), nullable=False)
    schedule_config = Column(JSON, nullable=False)  # Schedule configuration
    output_format = Column(String(20), nullable=False)
    parameters = Column(JSON, nullable=True)  # Default parameters
    recipients = Column(JSON, nullable=True)  # Email recipients
    is_active = Column(Boolean, default=True, nullable=False)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    template = relationship("ReportTemplate")
    creator = relationship("User")


# Pydantic Models for API
class ReportTemplateCreate(BaseModel):
    """Schema for creating report templates"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    report_type: ReportType
    template_config: Dict[str, Any] = Field(..., description="Template configuration")
    query_config: Dict[str, Any] = Field(..., description="Database query configuration")
    output_formats: List[ReportFormat] = Field(..., min_items=1)
    parameters: Optional[Dict[str, Any]] = None
    is_active: bool = True


class ReportTemplateUpdate(BaseModel):
    """Schema for updating report templates"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    report_type: Optional[ReportType] = None
    template_config: Optional[Dict[str, Any]] = None
    query_config: Optional[Dict[str, Any]] = None
    output_formats: Optional[List[ReportFormat]] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ReportTemplateResponse(BaseModel):
    """Schema for report template responses"""
    id: int
    name: str
    description: Optional[str]
    report_type: str
    template_config: Dict[str, Any]
    query_config: Dict[str, Any]
    output_formats: List[str]
    parameters: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


class ReportGenerateRequest(BaseModel):
    """Schema for generating reports"""
    template_name: Optional[str] = None
    report_type: ReportType
    output_format: ReportFormat
    parameters: Optional[Dict[str, Any]] = None
    custom_query: Optional[Dict[str, Any]] = None
    custom_template: Optional[Dict[str, Any]] = None


class ReportLogResponse(BaseModel):
    """Schema for report log responses"""
    id: int
    template_id: Optional[int]
    report_name: str
    report_type: str
    output_format: str
    status: str
    file_path: Optional[str]
    file_size: Optional[int]
    processing_time: Optional[float]
    record_count: Optional[int]
    generated_at: Optional[datetime]
    created_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


class ReportScheduleCreate(BaseModel):
    """Schema for creating report schedules"""
    template_name: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    frequency: ScheduleFrequency
    schedule_config: Dict[str, Any] = Field(..., description="Schedule configuration")
    output_format: ReportFormat
    parameters: Optional[Dict[str, Any]] = None
    recipients: Optional[List[str]] = None
    is_active: bool = True


class ReportScheduleUpdate(BaseModel):
    """Schema for updating report schedules"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    frequency: Optional[ScheduleFrequency] = None
    schedule_config: Optional[Dict[str, Any]] = None
    output_format: Optional[ReportFormat] = None
    parameters: Optional[Dict[str, Any]] = None
    recipients: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ReportScheduleResponse(BaseModel):
    """Schema for report schedule responses"""
    id: int
    template_id: Optional[int]
    name: str
    description: Optional[str]
    frequency: str
    schedule_config: Dict[str, Any]
    output_format: str
    parameters: Optional[Dict[str, Any]]
    recipients: Optional[List[str]]
    is_active: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


class ReportStats(BaseModel):
    """Schema for report statistics"""
    total_reports: int
    total_templates: int
    total_schedules: int
    reports_by_type: Dict[str, int]
    reports_by_status: Dict[str, int]
    reports_by_format: Dict[str, int]
    recent_reports: List[ReportLogResponse]
    processing_time_avg: float
    success_rate: float 