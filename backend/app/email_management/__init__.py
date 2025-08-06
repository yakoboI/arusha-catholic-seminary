"""
Email Management Module

This module provides comprehensive email notification and communication
capabilities for the Arusha Catholic Seminary School Management System.
"""

from .models import EmailTemplate, EmailLog
from .routes import router as email_router
from .services import EmailService

__all__ = [
    "EmailTemplate",
    "EmailLog", 
    "email_router",
    "EmailService"
] 