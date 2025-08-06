"""
Calendar Management Module

This module provides comprehensive calendar integration and event management
capabilities for the Arusha Catholic Seminary School Management System.
"""

from .models import CalendarEvent, EventCategory, EventParticipant
from .routes import router as calendar_router
from .services import CalendarService

__all__ = [
    "CalendarEvent",
    "EventCategory", 
    "EventParticipant",
    "calendar_router",
    "CalendarService"
] 