"""
File Management Module

This module provides comprehensive file upload, storage, and management
capabilities for the Arusha Catholic Seminary School Management System.
"""

from .models import FileRecord
from .routes import router as file_router
from .services import FileService

__all__ = [
    "FileRecord",
    "file_router", 
    "FileService"
] 