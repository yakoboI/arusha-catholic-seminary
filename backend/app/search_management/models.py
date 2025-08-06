"""
Search Management Models

This module defines the database models for search functionality
including search indices and search logs.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from ..database import Base


class SearchIndex(Base):
    """Search index model for full-text search"""
    __tablename__ = "search_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # student, teacher, class, etc.
    entity_id = Column(Integer, nullable=False, index=True)
    searchable_text = Column(Text, nullable=False)  # Combined searchable text
    metadata = Column(JSON, nullable=True)  # Additional search metadata
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes for better search performance
    __table_args__ = (
        Index('idx_search_text', 'searchable_text'),
        Index('idx_entity_type_id', 'entity_type', 'entity_id'),
    )


class SearchLog(Base):
    """Search log model for tracking search activity"""
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(500), nullable=False)
    entity_type = Column(String(50), nullable=True, index=True)
    filters = Column(JSON, nullable=True)  # Applied filters
    result_count = Column(Integer, nullable=False, default=0)
    search_time_ms = Column(Integer, nullable=False, default=0)  # Search execution time
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")


# Pydantic models for API requests/responses

class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    entity_type: Optional[str] = Field(None, description="Entity type to search in")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field("asc", regex="^(asc|desc)$", description="Sort order")


class SearchResponse(BaseModel):
    """Search response model"""
    query: str
    entity_type: Optional[str]
    results: list
    total_count: int
    page: int
    page_size: int
    total_pages: int
    search_time_ms: int
    filters_applied: Dict[str, Any]


class SearchIndexRequest(BaseModel):
    """Search index creation request"""
    entity_type: str = Field(..., description="Entity type")
    entity_id: int = Field(..., description="Entity ID")
    searchable_text: str = Field(..., description="Searchable text content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchStatistics(BaseModel):
    """Search statistics model"""
    total_searches: int
    searches_today: int
    searches_this_week: int
    searches_this_month: int
    average_search_time_ms: float
    most_searched_terms: list
    entity_type_distribution: Dict[str, int]
    user_search_activity: Dict[str, int]


class FilterOption(BaseModel):
    """Filter option model"""
    field: str
    label: str
    type: str  # text, select, date, number, boolean
    options: Optional[list] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    placeholder: Optional[str] = None


class EntitySearchConfig(BaseModel):
    """Entity search configuration"""
    entity_type: str
    searchable_fields: list
    filters: list[FilterOption]
    sort_options: list
    default_sort: str
    page_size_options: list[int] 