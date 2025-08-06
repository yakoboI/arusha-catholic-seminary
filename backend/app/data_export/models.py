"""
Data Export Models

This module defines the database models for data export functionality
including export jobs, templates, and configuration.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from enum import Enum

from ..database import Base


class ExportFormat(str, Enum):
    """Supported export formats"""
    CSV = "csv"
    EXCEL = "xlsx"
    PDF = "pdf"
    JSON = "json"
    XML = "xml"


class ExportStatus(str, Enum):
    """Export job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExportJob(Base):
    """Export job model"""
    __tablename__ = "export_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    entity_type = Column(String(50), nullable=False, index=True)  # student, teacher, class, etc.
    export_format = Column(String(20), nullable=False, index=True)
    filters = Column(JSON, nullable=True)  # Export filters
    columns = Column(JSON, nullable=True)  # Selected columns
    template_id = Column(Integer, ForeignKey("export_templates.id"), nullable=True)
    status = Column(String(20), default=ExportStatus.PENDING, nullable=False, index=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    record_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)  # Processing time in seconds
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    template = relationship("ExportTemplate")
    creator = relationship("User")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_export_status_created', 'status', 'created_at'),
        Index('idx_export_entity_type', 'entity_type', 'status'),
    )


class ExportTemplate(Base):
    """Export template model"""
    __tablename__ = "export_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    entity_type = Column(String(50), nullable=False, index=True)
    export_format = Column(String(20), nullable=False, index=True)
    columns = Column(JSON, nullable=False)  # Column configuration
    filters = Column(JSON, nullable=True)  # Default filters
    sorting = Column(JSON, nullable=True)  # Default sorting
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_default = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User")


# Pydantic models for API requests/responses

class ExportRequest(BaseModel):
    """Export request model"""
    name: str = Field(..., min_length=1, max_length=200, description="Export job name")
    description: Optional[str] = Field(None, description="Export job description")
    entity_type: str = Field(..., description="Entity type to export")
    export_format: ExportFormat = Field(..., description="Export format")
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")
    columns: Optional[List[str]] = Field(None, description="Selected columns")
    template_id: Optional[int] = Field(None, description="Export template ID")


class ExportResponse(BaseModel):
    """Export response model"""
    id: int
    name: str
    description: Optional[str]
    entity_type: str
    export_format: str
    status: str
    file_path: Optional[str]
    file_size: Optional[int]
    record_count: Optional[int]
    processing_time: Optional[float]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class ExportTemplateCreate(BaseModel):
    """Export template creation model"""
    name: str = Field(..., min_length=1, max_length=200, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    entity_type: str = Field(..., description="Entity type")
    export_format: ExportFormat = Field(..., description="Export format")
    columns: List[str] = Field(..., description="Column configuration")
    filters: Optional[Dict[str, Any]] = Field(None, description="Default filters")
    sorting: Optional[Dict[str, str]] = Field(None, description="Default sorting")
    is_default: bool = Field(False, description="Is default template")


class ExportTemplateResponse(BaseModel):
    """Export template response model"""
    id: int
    name: str
    description: Optional[str]
    entity_type: str
    export_format: str
    columns: List[str]
    filters: Optional[Dict[str, Any]]
    sorting: Optional[Dict[str, str]]
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime


class ExportStatistics(BaseModel):
    """Export statistics model"""
    total_exports: int
    exports_today: int
    exports_this_week: int
    exports_this_month: int
    average_processing_time: float
    format_distribution: Dict[str, int]
    entity_type_distribution: Dict[str, int]
    user_export_activity: Dict[str, int]


class ColumnDefinition(BaseModel):
    """Column definition model"""
    field: str
    label: str
    type: str  # text, number, date, boolean
    width: Optional[int] = None
    format: Optional[str] = None
    sortable: bool = True
    filterable: bool = True


class EntityExportConfig(BaseModel):
    """Entity export configuration"""
    entity_type: str
    available_columns: List[ColumnDefinition]
    default_columns: List[str]
    supported_formats: List[str]
    max_records: int
    batch_size: int 