"""
Calendar Management Routes

This module defines FastAPI routes for calendar operations including
event management, participant management, and calendar export.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from .models import (
    EventCategoryCreate, EventCategoryUpdate, EventCategoryResponse,
    CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse,
    EventParticipantCreate, EventParticipantUpdate, EventParticipantResponse,
    EventType, EventStatus, RecurrenceType
)
from .services import CalendarService

router = APIRouter(prefix="/api/v1/calendar", tags=["Calendar Management"])


# Event Category Routes
@router.post("/categories", response_model=EventCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_event_category(
    category: EventCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new event category"""
    try:
        service = CalendarService(db)
        category_data = category.dict()
        created_category = service.create_category(category_data, current_user.id)
        return EventCategoryResponse.from_orm(created_category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories", response_model=List[EventCategoryResponse])
async def get_event_categories(
    active_only: bool = Query(True, description="Return only active categories"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all event categories"""
    try:
        service = CalendarService(db)
        categories = service.get_categories(active_only=active_only)
        return [EventCategoryResponse.from_orm(cat) for cat in categories]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories/{category_id}", response_model=EventCategoryResponse)
async def get_event_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific event category"""
    try:
        service = CalendarService(db)
        category = service.get_category(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return EventCategoryResponse.from_orm(category)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/categories/{category_id}", response_model=EventCategoryResponse)
async def update_event_category(
    category_id: int,
    category: EventCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an event category"""
    try:
        service = CalendarService(db)
        category_data = {k: v for k, v in category.dict().items() if v is not None}
        updated_category = service.update_category(category_id, category_data)
        if not updated_category:
            raise HTTPException(status_code=404, detail="Category not found")
        return EventCategoryResponse.from_orm(updated_category)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an event category"""
    try:
        service = CalendarService(db)
        success = service.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Calendar Event Routes
@router.post("/events", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
async def create_calendar_event(
    event: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new calendar event"""
    try:
        service = CalendarService(db)
        event_data = event.dict()
        created_event = service.create_event(event_data, current_user.id)
        return CalendarEventResponse.from_orm(created_event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events", response_model=List[CalendarEventResponse])
async def get_calendar_events(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    event_type: Optional[EventType] = Query(None, description="Event type filter"),
    status: Optional[EventStatus] = Query(None, description="Event status filter"),
    category_id: Optional[int] = Query(None, description="Category filter"),
    user_id: Optional[int] = Query(None, description="User participation filter"),
    limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get calendar events with filtering"""
    try:
        service = CalendarService(db)
        events = service.get_events(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            status=status,
            category_id=category_id,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return [CalendarEventResponse.from_orm(event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events/{event_id}", response_model=CalendarEventResponse)
async def get_calendar_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific calendar event"""
    try:
        service = CalendarService(db)
        event = service.get_event(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return CalendarEventResponse.from_orm(event)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_calendar_event(
    event_id: int,
    event: CalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a calendar event"""
    try:
        service = CalendarService(db)
        event_data = {k: v for k, v in event.dict().items() if v is not None}
        updated_event = service.update_event(event_id, event_data)
        if not updated_event:
            raise HTTPException(status_code=404, detail="Event not found")
        return CalendarEventResponse.from_orm(updated_event)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a calendar event"""
    try:
        service = CalendarService(db)
        success = service.delete_event(event_id)
        if not success:
            raise HTTPException(status_code=404, detail="Event not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Event Participant Routes
@router.post("/events/{event_id}/participants", response_model=EventParticipantResponse, status_code=status.HTTP_201_CREATED)
async def add_event_participant(
    event_id: int,
    participant: EventParticipantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a participant to an event"""
    try:
        service = CalendarService(db)
        participant_data = participant.dict()
        created_participant = service.add_participant(
            event_id=event_id,
            user_id=participant_data["user_id"],
            role=participant_data.get("role", "attendee"),
            status=participant_data.get("status", "invited")
        )
        return EventParticipantResponse.from_orm(created_participant)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/events/{event_id}/participants/{user_id}", response_model=EventParticipantResponse)
async def update_participant_status(
    event_id: int,
    user_id: int,
    participant: EventParticipantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update participant status"""
    try:
        service = CalendarService(db)
        participant_data = {k: v for k, v in participant.dict().items() if v is not None}
        
        if "status" in participant_data:
            updated_participant = service.update_participant_status(
                event_id=event_id,
                user_id=user_id,
                status=participant_data["status"]
            )
            if not updated_participant:
                raise HTTPException(status_code=404, detail="Participant not found")
            return EventParticipantResponse.from_orm(updated_participant)
        else:
            raise HTTPException(status_code=400, detail="Status update required")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/events/{event_id}/participants/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_event_participant(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a participant from an event"""
    try:
        service = CalendarService(db)
        success = service.remove_participant(event_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Participant not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Calendar Export Routes
@router.get("/export/ical")
async def export_calendar_ical(
    user_id: Optional[int] = Query(None, description="Export events for specific user"),
    start_date: Optional[datetime] = Query(None, description="Start date for export"),
    end_date: Optional[datetime] = Query(None, description="End date for export"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export calendar events to iCal format"""
    try:
        service = CalendarService(db)
        ical_content = service.export_calendar_ical(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response(
            content=ical_content,
            media_type="text/calendar",
            headers={
                "Content-Disposition": "attachment; filename=calendar.ics"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Search and Statistics Routes
@router.get("/search")
async def search_events(
    q: str = Query(..., description="Search term"),
    user_id: Optional[int] = Query(None, description="Search in user's events"),
    limit: int = Query(50, ge=1, le=200, description="Number of results to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search events by title, description, or location"""
    try:
        service = CalendarService(db)
        events = service.search_events(
            search_term=q,
            user_id=user_id,
            limit=limit
        )
        return [CalendarEventResponse.from_orm(event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
async def get_calendar_stats(
    user_id: Optional[int] = Query(None, description="Stats for specific user"),
    start_date: Optional[datetime] = Query(None, description="Start date for stats"),
    end_date: Optional[datetime] = Query(None, description="End date for stats"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get calendar statistics"""
    try:
        service = CalendarService(db)
        stats = service.get_calendar_stats(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Quick Calendar Routes
@router.get("/upcoming")
async def get_upcoming_events(
    days: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    limit: int = Query(10, ge=1, le=50, description="Number of events to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming events for the current user"""
    try:
        service = CalendarService(db)
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days)
        
        events = service.get_events(
            start_date=start_date,
            end_date=end_date,
            user_id=current_user.id,
            limit=limit
        )
        return [CalendarEventResponse.from_orm(event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/today")
async def get_today_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get today's events for the current user"""
    try:
        service = CalendarService(db)
        today = datetime.utcnow().date()
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        
        events = service.get_events(
            start_date=start_date,
            end_date=end_date,
            user_id=current_user.id
        )
        return [CalendarEventResponse.from_orm(event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 