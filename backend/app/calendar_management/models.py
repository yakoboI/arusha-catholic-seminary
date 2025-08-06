"""
Calendar Management Models

This module defines the database models for calendar events, categories,
and participants in the Arusha Catholic Seminary School Management System.
"""

from datetime import datetime, time
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Time, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field, validator
from pydantic.types import constr

from ..database import Base


class EventType(str, Enum):
    """Event type enumeration"""
    ACADEMIC = "academic"
    SPIRITUAL = "spiritual"
    ADMINISTRATIVE = "administrative"
    SOCIAL = "social"
    SPORTS = "sports"
    CULTURAL = "cultural"
    MEETING = "meeting"
    EXAM = "exam"
    HOLIDAY = "holiday"
    OTHER = "other"


class EventStatus(str, Enum):
    """Event status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class RecurrenceType(str, Enum):
    """Recurrence type enumeration"""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class EventCategory(Base):
    """Event category model"""
    __tablename__ = "event_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=False, default="#3B82F6")  # Hex color
    icon = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    events = relationship("CalendarEvent", back_populates="category")
    creator = relationship("User")


class CalendarEvent(Base):
    """Calendar event model"""
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), default=EventStatus.DRAFT, nullable=False, index=True)
    
    # Date and time
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    all_day = Column(Boolean, default=False, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    
    # Location
    location = Column(String(200), nullable=True)
    room = Column(String(100), nullable=True)
    
    # Recurrence
    recurrence_type = Column(String(20), default=RecurrenceType.NONE, nullable=False)
    recurrence_config = Column(JSON, nullable=True)  # For complex recurrence rules
    
    # Category and organization
    category_id = Column(Integer, ForeignKey("event_categories.id"), nullable=True)
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, urgent
    
    # Additional metadata
    tags = Column(JSON, nullable=True)  # Array of tags
    attachments = Column(JSON, nullable=True)  # Array of file IDs
    metadata = Column(JSON, nullable=True)  # Additional custom data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    category = relationship("EventCategory", back_populates="events")
    creator = relationship("User")
    participants = relationship("EventParticipant", back_populates="event", cascade="all, delete-orphan")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_event_date_range', 'start_date', 'end_date'),
        Index('idx_event_type_status', 'event_type', 'status'),
        Index('idx_event_category', 'category_id'),
    )


class EventParticipant(Base):
    """Event participant model"""
    __tablename__ = "event_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False, default="attendee")  # organizer, attendee, presenter
    status = Column(String(20), nullable=False, default="invited")  # invited, accepted, declined, tentative
    response_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("CalendarEvent", back_populates="participants")
    user = relationship("User")
    
    # Unique constraint to prevent duplicate participants
    __table_args__ = (
        Index('idx_participant_unique', 'event_id', 'user_id', unique=True),
    )


# Pydantic Models for API
class EventCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: str = Field(default="#3B82F6", regex=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class EventCategoryCreate(EventCategoryBase):
    pass


class EventCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, regex=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class EventCategoryResponse(EventCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class CalendarEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: EventType
    status: EventStatus = EventStatus.DRAFT
    start_date: datetime
    end_date: datetime
    all_day: bool = False
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = Field(None, max_length=200)
    room: Optional[str] = Field(None, max_length=100)
    recurrence_type: RecurrenceType = RecurrenceType.NONE
    recurrence_config: Optional[Dict[str, Any]] = None
    category_id: Optional[int] = None
    priority: str = Field(default="normal", regex=r"^(low|normal|high|urgent)$")
    tags: Optional[List[str]] = None
    attachments: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if not values.get('all_day') and 'start_time' in values and v and values['start_time'] and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    all_day: Optional[bool] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = Field(None, max_length=200)
    room: Optional[str] = Field(None, max_length=100)
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_config: Optional[Dict[str, Any]] = None
    category_id: Optional[int] = None
    priority: Optional[str] = Field(None, regex=r"^(low|normal|high|urgent)$")
    tags: Optional[List[str]] = None
    attachments: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None


class CalendarEventResponse(CalendarEventBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    category: Optional[EventCategoryResponse] = None
    participants: List['EventParticipantResponse'] = []
    
    class Config:
        from_attributes = True


class EventParticipantBase(BaseModel):
    user_id: int
    role: str = Field(default="attendee", regex=r"^(organizer|attendee|presenter)$")
    status: str = Field(default="invited", regex=r"^(invited|accepted|declined|tentative)$")
    notes: Optional[str] = None


class EventParticipantCreate(EventParticipantBase):
    pass


class EventParticipantUpdate(BaseModel):
    role: Optional[str] = Field(None, regex=r"^(organizer|attendee|presenter)$")
    status: Optional[str] = Field(None, regex=r"^(invited|accepted|declined|tentative)$")
    notes: Optional[str] = None


class EventParticipantResponse(EventParticipantBase):
    id: int
    event_id: int
    response_date: Optional[datetime] = None
    created_at: datetime
    user: Dict[str, Any]  # Basic user info
    
    class Config:
        from_attributes = True


# Update forward references
CalendarEventResponse.update_forward_refs() 