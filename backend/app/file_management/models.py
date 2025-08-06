"""
File Management Models

Database models for file upload and management system.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from app.database import Base


class FileCategory(str, Enum):
    """File categories for organization"""
    ACADEMIC_RECORD = "academic_record"
    CERTIFICATE = "certificate"
    PHOTO = "photo"
    ASSIGNMENT = "assignment"
    REPORT = "report"
    DOCUMENT = "document"
    OTHER = "other"


class FileRecord(Base):
    """Database model for file records"""
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_extension = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False, default=FileCategory.OTHER)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string of tags
    
    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Related entity (optional)
    related_entity_type = Column(String(50), nullable=True)  # student, teacher, class, etc.
    related_entity_id = Column(Integer, nullable=True)
    
    # File processing
    is_processed = Column(Boolean, default=False, nullable=False)
    processing_status = Column(String(50), default="pending", nullable=False)
    processing_errors = Column(Text, nullable=True)
    
    # Security
    checksum = Column(String(64), nullable=True)  # SHA-256 hash
    virus_scan_status = Column(String(20), default="pending", nullable=False)
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_files")


# Pydantic models for API
class FileRecordBase(BaseModel):
    """Base file record model"""
    filename: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: FileCategory = Field(default=FileCategory.OTHER)
    tags: Optional[str] = Field(None, max_length=500)
    is_public: bool = Field(default=False)
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[int] = Field(None, ge=1)


class FileRecordCreate(FileRecordBase):
    """Model for creating file records"""
    pass


class FileRecordUpdate(BaseModel):
    """Model for updating file records"""
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[FileCategory] = None
    tags: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[int] = Field(None, ge=1)


class FileRecordResponse(FileRecordBase):
    """Model for file record responses"""
    id: int
    original_filename: str
    file_size: int
    mime_type: str
    file_extension: str
    uploaded_by: int
    uploaded_at: datetime
    is_deleted: bool
    is_processed: bool
    processing_status: str
    virus_scan_status: str
    checksum: Optional[str] = None
    uploader_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Model for file upload responses"""
    file_record: FileRecordResponse
    download_url: str
    preview_url: Optional[str] = None


class FileListResponse(BaseModel):
    """Model for file list responses"""
    files: list[FileRecordResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class FileSearchParams(BaseModel):
    """Model for file search parameters"""
    query: Optional[str] = Field(None, max_length=100)
    category: Optional[FileCategory] = None
    uploaded_by: Optional[int] = Field(None, ge=1)
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[int] = Field(None, ge=1)
    is_public: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="uploaded_at", regex="^(filename|file_size|uploaded_at|category)$")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$") 