"""
Search Management Module

This module provides comprehensive search and filtering capabilities
for the Arusha Catholic Seminary School Management System.
"""

from .models import SearchIndex, SearchLog
from .routes import router as search_router
from .services import SearchService

__all__ = [
    "SearchIndex",
    "SearchLog", 
    "search_router",
    "SearchService"
] 