"""
Email Management Services

This module provides the core business logic for email operations
including template management, email sending, and logging.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from jinja2 import Template, Environment, BaseLoader
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

from ..config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    EMAIL_FROM, EMAIL_FROM_NAME, EMAIL_RATE_LIMIT
)
from ..models import User
from .models import (
    EmailTemplate, EmailLog, EmailType, EmailStatus,
    EmailTemplateCreate, EmailTemplateUpdate, EmailSendRequest,
    EmailBulkSendRequest, EmailStats
)

logger = logging.getLogger(__name__)


class EmailService:
    """Service class for email operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.jinja_env = Environment(loader=BaseLoader())
        self.rate_limit_counter = 0
        self.last_reset = datetime.utcnow()
    
    def _check_rate_limit(self) -> bool:
        """Check if email sending is within rate limits"""
        now = datetime.utcnow()
        if now - self.last_reset > timedelta(hours=1):
            self.rate_limit_counter = 0
            self.last_reset = now
        
        if self.rate_limit_counter >= EMAIL_RATE_LIMIT:
            return False
        
        self.rate_limit_counter += 1
        return True
    
    def _render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """Render Jinja2 template with variables"""
        try:
            template = self.jinja_env.from_string(template_content)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return template_content
    
    def create_template(self, template_data: EmailTemplateCreate, user: User) -> EmailTemplate:
        """Create a new email template"""
        template = EmailTemplate(
            name=template_data.name,
            subject=template_data.subject,
            body_html=template_data.body_html,
            body_text=template_data.body_text,
            email_type=template_data.email_type.value,
            variables=template_data.variables,
            is_active=template_data.is_active,
            created_by=user.id
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        logger.info(f"Email template created: {template.name}")
        return template
    
    def get_template(self, template_id: int) -> Optional[EmailTemplate]:
        """Get email template by ID"""
        return self.db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    
    def get_template_by_name(self, name: str) -> Optional[EmailTemplate]:
        """Get email template by name"""
        return self.db.query(EmailTemplate).filter(
            EmailTemplate.name == name,
            EmailTemplate.is_active == True
        ).first()
    
    def list_templates(
        self, 
        skip: int = 0, 
        limit: int = 100,
        email_type: Optional[EmailType] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[EmailTemplate], int]:
        """List email templates with filtering and pagination"""
        query = self.db.query(EmailTemplate)
        
        if email_type:
            query = query.filter(EmailTemplate.email_type == email_type.value)
        
        if is_active is not None:
            query = query.filter(EmailTemplate.is_active == is_active)
        
        total = query.count()
        templates = query.offset(skip).limit(limit).all()
        
        return templates, total
    
    def update_template(
        self, 
        template_id: int, 
        template_data: EmailTemplateUpdate
    ) -> Optional[EmailTemplate]:
        """Update email template"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        update_data = template_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(template)
        
        logger.info(f"Email template updated: {template.name}")
        return template
    
    def delete_template(self, template_id: int) -> bool:
        """Delete email template (soft delete by deactivating)"""
        template = self.get_template(template_id)
        if not template:
            return False
        
        template.is_active = False
        template.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Email template deactivated: {template.name}")
        return True
    
    def create_email_log(
        self,
        recipient_email: str,
        recipient_name: Optional[str],
        subject: str,
        body_html: str,
        body_text: Optional[str],
        email_type: EmailType,
        template_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        sent_by: Optional[int] = None
    ) -> EmailLog:
        """Create email log entry"""
        email_log = EmailLog(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            email_type=email_type.value,
            template_id=template_id,
            metadata=metadata,
            sent_by=sent_by
        )
        
        self.db.add(email_log)
        self.db.commit()
        self.db.refresh(email_log)
        
        return email_log
    
    async def send_email(
        self,
        recipient_email: str,
        recipient_name: Optional[str],
        subject: str,
        body_html: str,
        body_text: Optional[str],
        email_type: EmailType,
        template_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        sent_by: Optional[int] = None
    ) -> bool:
        """Send email asynchronously"""
        if not self._check_rate_limit():
            logger.warning("Email rate limit exceeded")
            return False
        
        # Create email log
        email_log = self.create_email_log(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            email_type=email_type,
            template_id=template_id,
            metadata=metadata,
            sent_by=sent_by
        )
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = formataddr((EMAIL_FROM_NAME, EMAIL_FROM))
            message["To"] = formataddr((recipient_name or recipient_email, recipient_email))
            message["Subject"] = subject
            
            # Add HTML and text parts
            if body_html:
                html_part = MIMEText(body_html, "html")
                message.attach(html_part)
            
            if body_text:
                text_part = MIMEText(body_text, "plain")
                message.attach(text_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USER,
                password=SMTP_PASSWORD,
                use_tls=True
            )
            
            # Update log status
            email_log.status = EmailStatus.SENT
            email_log.sent_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            # Update log with error
            email_log.status = EmailStatus.FAILED
            email_log.error_message = str(e)
            email_log.retry_count += 1
            self.db.commit()
            
            logger.error(f"Email sending failed to {recipient_email}: {e}")
            return False
    
    async def send_email_with_template(
        self,
        request: EmailSendRequest,
        user: User
    ) -> bool:
        """Send email using template"""
        template = None
        if request.template_name:
            template = self.get_template_by_name(request.template_name)
        
        if template:
            # Render template with variables
            subject = self._render_template(template.subject, request.variables or {})
            body_html = self._render_template(template.body_html, request.variables or {})
            body_text = None
            if template.body_text:
                body_text = self._render_template(template.body_text, request.variables or {})
        else:
            # Use direct content
            subject = request.subject
            body_html = request.body_html
            body_text = request.body_text
        
        if not subject or not body_html:
            logger.error("Missing subject or body for email")
            return False
        
        return await self.send_email(
            recipient_email=request.recipient_email,
            recipient_name=request.recipient_name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            email_type=request.email_type,
            template_id=template.id if template else None,
            metadata=request.metadata,
            sent_by=user.id
        )
    
    async def send_bulk_emails(
        self,
        request: EmailBulkSendRequest,
        user: User
    ) -> Dict[str, Any]:
        """Send bulk emails"""
        results = {
            "total": len(request.recipient_emails),
            "sent": 0,
            "failed": 0,
            "errors": []
        }
        
        template = None
        if request.template_name:
            template = self.get_template_by_name(request.template_name)
        
        if template:
            subject = self._render_template(template.subject, request.variables or {})
            body_html = self._render_template(template.body_html, request.variables or {})
            body_text = None
            if template.body_text:
                body_text = self._render_template(template.body_text, request.variables or {})
        else:
            subject = request.subject
            body_html = request.body_html
            body_text = request.body_text
        
        if not subject or not body_html:
            results["errors"].append("Missing subject or body for email")
            return results
        
        # Send emails concurrently
        tasks = []
        for recipient_email in request.recipient_emails:
            task = self.send_email(
                recipient_email=recipient_email,
                recipient_name=None,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                email_type=request.email_type,
                template_id=template.id if template else None,
                metadata=request.metadata,
                sent_by=user.id
            )
            tasks.append(task)
        
        # Wait for all emails to be sent
        email_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(email_results):
            if isinstance(result, Exception):
                results["failed"] += 1
                results["errors"].append(f"Email {i+1}: {str(result)}")
            elif result:
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"Email {i+1}: Failed to send")
        
        logger.info(f"Bulk email completed: {results['sent']} sent, {results['failed']} failed")
        return results
    
    def get_email_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        email_type: Optional[EmailType] = None,
        status: Optional[EmailStatus] = None,
        recipient_email: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[EmailLog], int]:
        """Get email logs with filtering and pagination"""
        query = self.db.query(EmailLog)
        
        if email_type:
            query = query.filter(EmailLog.email_type == email_type.value)
        
        if status:
            query = query.filter(EmailLog.status == status.value)
        
        if recipient_email:
            query = query.filter(EmailLog.recipient_email.contains(recipient_email))
        
        if start_date:
            query = query.filter(EmailLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(EmailLog.created_at <= end_date)
        
        total = query.count()
        logs = query.order_by(desc(EmailLog.created_at)).offset(skip).limit(limit).all()
        
        return logs, total
    
    def get_email_stats(self, days: int = 30) -> EmailStats:
        """Get email statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic counts
        total_sent = self.db.query(EmailLog).filter(
            EmailLog.created_at >= start_date
        ).count()
        
        total_delivered = self.db.query(EmailLog).filter(
            and_(
                EmailLog.created_at >= start_date,
                EmailLog.status == EmailStatus.DELIVERED
            )
        ).count()
        
        total_failed = self.db.query(EmailLog).filter(
            and_(
                EmailLog.created_at >= start_date,
                EmailLog.status == EmailStatus.FAILED
            )
        ).count()
        
        total_pending = self.db.query(EmailLog).filter(
            and_(
                EmailLog.created_at >= start_date,
                EmailLog.status == EmailStatus.PENDING
            )
        ).count()
        
        # Calculate rates
        delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
        failure_rate = (total_failed / total_sent * 100) if total_sent > 0 else 0
        
        # Emails by type
        emails_by_type = {}
        type_counts = self.db.query(
            EmailLog.email_type,
            func.count(EmailLog.id)
        ).filter(
            EmailLog.created_at >= start_date
        ).group_by(EmailLog.email_type).all()
        
        for email_type, count in type_counts:
            emails_by_type[email_type] = count
        
        # Emails by status
        emails_by_status = {}
        status_counts = self.db.query(
            EmailLog.status,
            func.count(EmailLog.id)
        ).filter(
            EmailLog.created_at >= start_date
        ).group_by(EmailLog.status).all()
        
        for status, count in status_counts:
            emails_by_status[status] = count
        
        # Recent activity
        recent_activity = self.db.query(EmailLog).filter(
            EmailLog.created_at >= start_date
        ).order_by(desc(EmailLog.created_at)).limit(10).all()
        
        return EmailStats(
            total_sent=total_sent,
            total_delivered=total_delivered,
            total_failed=total_failed,
            total_pending=total_pending,
            delivery_rate=delivery_rate,
            failure_rate=failure_rate,
            emails_by_type=emails_by_type,
            emails_by_status=emails_by_status,
            recent_activity=recent_activity
        )
    
    def retry_failed_emails(self, max_retries: int = 3) -> Dict[str, int]:
        """Retry failed emails"""
        failed_emails = self.db.query(EmailLog).filter(
            and_(
                EmailLog.status == EmailStatus.FAILED,
                EmailLog.retry_count < max_retries
            )
        ).all()
        
        retry_count = 0
        success_count = 0
        
        for email_log in failed_emails:
            retry_count += 1
            # Here you would implement the actual retry logic
            # For now, we'll just mark them as pending for manual review
            email_log.status = EmailStatus.PENDING
            email_log.retry_count += 1
        
        self.db.commit()
        
        logger.info(f"Retried {retry_count} failed emails")
        return {"retried": retry_count, "successful": success_count} 