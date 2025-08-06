"""
Email Management Routes

This module defines FastAPI routes for email operations including
template management, email sending, and logging.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from .models import (
    EmailTemplate, EmailLog, EmailType, EmailStatus,
    EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse,
    EmailSendRequest, EmailBulkSendRequest, EmailLogResponse, EmailStats
)
from .services import EmailService

router = APIRouter(prefix="/api/v1/email", tags=["Email Management"])


# Template Management Endpoints
@router.post("/templates", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_email_template(
    template_data: EmailTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new email template"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can create email templates"
        )
    
    email_service = EmailService(db)
    template = email_service.create_template(template_data, current_user)
    return template


@router.get("/templates", response_model=List[EmailTemplateResponse])
async def list_email_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    email_type: Optional[EmailType] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List email templates with filtering and pagination"""
    email_service = EmailService(db)
    templates, total = email_service.list_templates(skip, limit, email_type, is_active)
    return templates


@router.get("/templates/{template_id}", response_model=EmailTemplateResponse)
async def get_email_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email template by ID"""
    email_service = EmailService(db)
    template = email_service.get_template(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found"
        )
    
    return template


@router.put("/templates/{template_id}", response_model=EmailTemplateResponse)
async def update_email_template(
    template_id: int,
    template_data: EmailTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update email template"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can update email templates"
        )
    
    email_service = EmailService(db)
    template = email_service.update_template(template_id, template_data)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found"
        )
    
    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete email template (soft delete)"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can delete email templates"
        )
    
    email_service = EmailService(db)
    success = email_service.delete_template(template_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found"
        )


# Email Sending Endpoints
@router.post("/send", status_code=status.HTTP_200_OK)
async def send_email(
    request: EmailSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a single email"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can send emails"
        )
    
    email_service = EmailService(db)
    success = await email_service.send_email_with_template(request, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )
    
    return {"message": "Email sent successfully"}


@router.post("/send/bulk", status_code=status.HTTP_200_OK)
async def send_bulk_emails(
    request: EmailBulkSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send bulk emails"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can send bulk emails"
        )
    
    email_service = EmailService(db)
    results = await email_service.send_bulk_emails(request, current_user)
    
    return {
        "message": "Bulk email operation completed",
        "results": results
    }


# Email Logs Endpoints
@router.get("/logs", response_model=List[EmailLogResponse])
async def get_email_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    email_type: Optional[EmailType] = Query(None),
    status: Optional[EmailStatus] = Query(None),
    recipient_email: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email logs with filtering and pagination"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can view email logs"
        )
    
    email_service = EmailService(db)
    logs, total = email_service.get_email_logs(
        skip, limit, email_type, status, recipient_email, start_date, end_date
    )
    return logs


@router.get("/logs/{log_id}", response_model=EmailLogResponse)
async def get_email_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific email log by ID"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can view email logs"
        )
    
    log = db.query(EmailLog).filter(EmailLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email log not found"
        )
    
    return log


# Email Statistics Endpoints
@router.get("/stats", response_model=EmailStats)
async def get_email_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email statistics"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can view email statistics"
        )
    
    email_service = EmailService(db)
    stats = email_service.get_email_stats(days)
    return stats


# Email Management Endpoints
@router.post("/retry-failed", status_code=status.HTTP_200_OK)
async def retry_failed_emails(
    max_retries: int = Query(3, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retry failed emails"""
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can retry failed emails"
        )
    
    email_service = EmailService(db)
    results = email_service.retry_failed_emails(max_retries)
    
    return {
        "message": "Failed email retry operation completed",
        "results": results
    }


# Email Types Endpoint
@router.get("/types", status_code=status.HTTP_200_OK)
async def get_email_types():
    """Get available email types"""
    return {
        "email_types": [
            {"value": email_type.value, "label": email_type.value.replace("_", " ").title()}
            for email_type in EmailType
        ]
    }


# Email Statuses Endpoint
@router.get("/statuses", status_code=status.HTTP_200_OK)
async def get_email_statuses():
    """Get available email statuses"""
    return {
        "email_statuses": [
            {"value": status.value, "label": status.value.replace("_", " ").title()}
            for status in EmailStatus
        ]
    }


# Template Preview Endpoint
@router.post("/templates/{template_id}/preview", status_code=status.HTTP_200_OK)
async def preview_email_template(
    template_id: int,
    variables: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview email template with variables"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can preview email templates"
        )
    
    email_service = EmailService(db)
    template = email_service.get_template(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found"
        )
    
    try:
        subject = email_service._render_template(template.subject, variables)
        body_html = email_service._render_template(template.body_html, variables)
        body_text = None
        if template.body_text:
            body_text = email_service._render_template(template.body_text, variables)
        
        return {
            "subject": subject,
            "body_html": body_html,
            "body_text": body_text
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template rendering error: {str(e)}"
        ) 