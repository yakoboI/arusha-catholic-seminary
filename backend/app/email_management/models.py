"""
Email Management Models

This module defines the database models and Pydantic schemas for
email templates, logs, and notifications.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field
from ..database import Base


class EmailType(str, Enum):
    """Email notification types"""
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"
    GRADE_UPDATE = "grade_update"
    ATTENDANCE_ALERT = "attendance_alert"
    EVENT_REMINDER = "event_reminder"
    SYSTEM_NOTIFICATION = "system_notification"
    BULK_ANNOUNCEMENT = "bulk_announcement"
    DAILY_REPORT = "daily_report"
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_REPORT = "monthly_report"


class EmailStatus(str, Enum):
    """Email delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


class EmailTemplate(Base):
    """Database model for email templates"""
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    subject = Column(String(200), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    email_type = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    variables = Column(JSON, nullable=True)  # Template variables
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class EmailLog(Base):
    """Database model for email logs"""
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_email = Column(String(255), nullable=False, index=True)
    recipient_name = Column(String(100), nullable=True)
    subject = Column(String(200), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    email_type = Column(String(50), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=True)
    status = Column(String(20), default=EmailStatus.PENDING, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    metadata = Column(JSON, nullable=True)  # Additional data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    template = relationship("EmailTemplate")
    sender = relationship("User")


# Pydantic Models for API
class EmailTemplateCreate(BaseModel):
    """Schema for creating email templates"""
    name: str = Field(..., min_length=1, max_length=100)
    subject: str = Field(..., min_length=1, max_length=200)
    body_html: str = Field(..., min_length=1)
    body_text: Optional[str] = None
    email_type: EmailType
    variables: Optional[Dict[str, Any]] = None
    is_active: bool = True


class EmailTemplateUpdate(BaseModel):
    """Schema for updating email templates"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    body_html: Optional[str] = Field(None, min_length=1)
    body_text: Optional[str] = None
    email_type: Optional[EmailType] = None
    variables: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class EmailTemplateResponse(BaseModel):
    """Schema for email template responses"""
    id: int
    name: str
    subject: str
    body_html: str
    body_text: Optional[str]
    email_type: str
    is_active: bool
    variables: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


class EmailSendRequest(BaseModel):
    """Schema for sending emails"""
    recipient_email: EmailStr
    recipient_name: Optional[str] = None
    template_name: Optional[str] = None
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    email_type: EmailType
    variables: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class EmailBulkSendRequest(BaseModel):
    """Schema for bulk email sending"""
    recipient_emails: List[EmailStr] = Field(..., min_items=1, max_items=100)
    template_name: Optional[str] = None
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    email_type: EmailType
    variables: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class EmailLogResponse(BaseModel):
    """Schema for email log responses"""
    id: int
    recipient_email: str
    recipient_name: Optional[str]
    subject: str
    email_type: str
    status: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    sent_by: Optional[int]

    class Config:
        from_attributes = True


class EmailStats(BaseModel):
    """Schema for email statistics"""
    total_sent: int
    total_delivered: int
    total_failed: int
    total_pending: int
    delivery_rate: float
    failure_rate: float
    emails_by_type: Dict[str, int]
    emails_by_status: Dict[str, int]
    recent_activity: List[EmailLogResponse] 