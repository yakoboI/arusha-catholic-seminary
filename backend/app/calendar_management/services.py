"""
Calendar Management Services

This module provides business logic for calendar operations including
event management, recurrence handling, and calendar export capabilities.
"""

import logging
from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from icalendar import Calendar, Event as ICalEvent
import pytz

from .models import (
    CalendarEvent, EventCategory, EventParticipant,
    EventType, EventStatus, RecurrenceType
)
from ..models import User

logger = logging.getLogger(__name__)


class CalendarService:
    """Service class for calendar operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Event Category Management
    def create_category(self, category_data: Dict[str, Any], created_by: int) -> EventCategory:
        """Create a new event category"""
        try:
            category = EventCategory(
                name=category_data["name"],
                description=category_data.get("description"),
                color=category_data.get("color", "#3B82F6"),
                icon=category_data.get("icon"),
                created_by=created_by
            )
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            logger.info(f"Created event category: {category.name}")
            return category
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating event category: {e}")
            raise
    
    def get_categories(self, active_only: bool = True) -> List[EventCategory]:
        """Get all event categories"""
        query = self.db.query(EventCategory)
        if active_only:
            query = query.filter(EventCategory.is_active == True)
        return query.order_by(EventCategory.name).all()
    
    def get_category(self, category_id: int) -> Optional[EventCategory]:
        """Get a specific event category"""
        return self.db.query(EventCategory).filter(EventCategory.id == category_id).first()
    
    def update_category(self, category_id: int, category_data: Dict[str, Any]) -> Optional[EventCategory]:
        """Update an event category"""
        try:
            category = self.get_category(category_id)
            if not category:
                return None
            
            for key, value in category_data.items():
                if hasattr(category, key) and value is not None:
                    setattr(category, key, value)
            
            self.db.commit()
            self.db.refresh(category)
            logger.info(f"Updated event category: {category.name}")
            return category
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating event category: {e}")
            raise
    
    def delete_category(self, category_id: int) -> bool:
        """Delete an event category"""
        try:
            category = self.get_category(category_id)
            if not category:
                return False
            
            # Check if category has events
            event_count = self.db.query(CalendarEvent).filter(
                CalendarEvent.category_id == category_id
            ).count()
            
            if event_count > 0:
                raise ValueError(f"Cannot delete category with {event_count} events")
            
            self.db.delete(category)
            self.db.commit()
            logger.info(f"Deleted event category: {category.name}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting event category: {e}")
            raise
    
    # Event Management
    def create_event(self, event_data: Dict[str, Any], created_by: int) -> CalendarEvent:
        """Create a new calendar event"""
        try:
            # Handle time fields for all-day events
            if event_data.get("all_day"):
                event_data["start_time"] = None
                event_data["end_time"] = None
            
            event = CalendarEvent(
                title=event_data["title"],
                description=event_data.get("description"),
                event_type=event_data["event_type"],
                status=event_data.get("status", EventStatus.DRAFT),
                start_date=event_data["start_date"],
                end_date=event_data["end_date"],
                all_day=event_data.get("all_day", False),
                start_time=event_data.get("start_time"),
                end_time=event_data.get("end_time"),
                location=event_data.get("location"),
                room=event_data.get("room"),
                recurrence_type=event_data.get("recurrence_type", RecurrenceType.NONE),
                recurrence_config=event_data.get("recurrence_config"),
                category_id=event_data.get("category_id"),
                priority=event_data.get("priority", "normal"),
                tags=event_data.get("tags"),
                attachments=event_data.get("attachments"),
                metadata=event_data.get("metadata"),
                created_by=created_by
            )
            
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            
            # Add creator as organizer participant
            self.add_participant(event.id, created_by, "organizer", "accepted")
            
            logger.info(f"Created calendar event: {event.title}")
            return event
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating calendar event: {e}")
            raise
    
    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[EventType] = None,
        status: Optional[EventStatus] = None,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CalendarEvent]:
        """Get calendar events with filtering"""
        query = self.db.query(CalendarEvent).options(
            joinedload(CalendarEvent.category),
            joinedload(CalendarEvent.participants).joinedload(EventParticipant.user)
        )
        
        # Date range filter
        if start_date and end_date:
            query = query.filter(
                and_(
                    CalendarEvent.start_date >= start_date,
                    CalendarEvent.end_date <= end_date
                )
            )
        elif start_date:
            query = query.filter(CalendarEvent.start_date >= start_date)
        elif end_date:
            query = query.filter(CalendarEvent.end_date <= end_date)
        
        # Type and status filters
        if event_type:
            query = query.filter(CalendarEvent.event_type == event_type)
        if status:
            query = query.filter(CalendarEvent.status == status)
        if category_id:
            query = query.filter(CalendarEvent.category_id == category_id)
        
        # User participation filter
        if user_id:
            query = query.join(EventParticipant).filter(
                EventParticipant.user_id == user_id
            )
        
        return query.order_by(CalendarEvent.start_date).offset(offset).limit(limit).all()
    
    def get_event(self, event_id: int) -> Optional[CalendarEvent]:
        """Get a specific calendar event"""
        return self.db.query(CalendarEvent).options(
            joinedload(CalendarEvent.category),
            joinedload(CalendarEvent.participants).joinedload(EventParticipant.user)
        ).filter(CalendarEvent.id == event_id).first()
    
    def update_event(self, event_id: int, event_data: Dict[str, Any]) -> Optional[CalendarEvent]:
        """Update a calendar event"""
        try:
            event = self.get_event(event_id)
            if not event:
                return None
            
            # Handle time fields for all-day events
            if event_data.get("all_day"):
                event_data["start_time"] = None
                event_data["end_time"] = None
            
            for key, value in event_data.items():
                if hasattr(event, key) and value is not None:
                    setattr(event, key, value)
            
            self.db.commit()
            self.db.refresh(event)
            logger.info(f"Updated calendar event: {event.title}")
            return event
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating calendar event: {e}")
            raise
    
    def delete_event(self, event_id: int) -> bool:
        """Delete a calendar event"""
        try:
            event = self.get_event(event_id)
            if not event:
                return False
            
            self.db.delete(event)
            self.db.commit()
            logger.info(f"Deleted calendar event: {event.title}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting calendar event: {e}")
            raise
    
    # Participant Management
    def add_participant(self, event_id: int, user_id: int, role: str = "attendee", status: str = "invited") -> EventParticipant:
        """Add a participant to an event"""
        try:
            # Check if participant already exists
            existing = self.db.query(EventParticipant).filter(
                and_(
                    EventParticipant.event_id == event_id,
                    EventParticipant.user_id == user_id
                )
            ).first()
            
            if existing:
                raise ValueError("Participant already exists for this event")
            
            participant = EventParticipant(
                event_id=event_id,
                user_id=user_id,
                role=role,
                status=status
            )
            
            self.db.add(participant)
            self.db.commit()
            self.db.refresh(participant)
            logger.info(f"Added participant {user_id} to event {event_id}")
            return participant
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding participant: {e}")
            raise
    
    def update_participant_status(self, event_id: int, user_id: int, status: str) -> Optional[EventParticipant]:
        """Update participant status"""
        try:
            participant = self.db.query(EventParticipant).filter(
                and_(
                    EventParticipant.event_id == event_id,
                    EventParticipant.user_id == user_id
                )
            ).first()
            
            if not participant:
                return None
            
            participant.status = status
            participant.response_date = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(participant)
            logger.info(f"Updated participant {user_id} status to {status} for event {event_id}")
            return participant
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating participant status: {e}")
            raise
    
    def remove_participant(self, event_id: int, user_id: int) -> bool:
        """Remove a participant from an event"""
        try:
            participant = self.db.query(EventParticipant).filter(
                and_(
                    EventParticipant.event_id == event_id,
                    EventParticipant.user_id == user_id
                )
            ).first()
            
            if not participant:
                return False
            
            self.db.delete(participant)
            self.db.commit()
            logger.info(f"Removed participant {user_id} from event {event_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing participant: {e}")
            raise
    
    # Calendar Export
    def export_calendar_ical(self, user_id: Optional[int] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """Export calendar events to iCal format"""
        try:
            # Get events
            events = self.get_events(start_date=start_date, end_date=end_date, user_id=user_id)
            
            # Create iCal calendar
            cal = Calendar()
            cal.add('prodid', '-//Arusha Catholic Seminary//Calendar//EN')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            
            for event in events:
                ical_event = ICalEvent()
                ical_event.add('summary', event.title)
                
                if event.description:
                    ical_event.add('description', event.description)
                
                if event.location:
                    ical_event.add('location', event.location)
                
                # Handle all-day events
                if event.all_day:
                    ical_event.add('dtstart', event.start_date.date())
                    ical_event.add('dtend', event.end_date.date())
                else:
                    # Combine date and time
                    start_dt = datetime.combine(event.start_date.date(), event.start_time or time(0, 0))
                    end_dt = datetime.combine(event.end_date.date(), event.end_time or time(23, 59))
                    ical_event.add('dtstart', start_dt)
                    ical_event.add('dtend', end_dt)
                
                ical_event.add('uid', f"event-{event.id}@arushaseminary.edu")
                ical_event.add('dtstamp', datetime.utcnow())
                
                # Add recurrence if applicable
                if event.recurrence_type != RecurrenceType.NONE and event.recurrence_config:
                    rrule = self._build_rrule(event.recurrence_type, event.recurrence_config)
                    if rrule:
                        ical_event.add('rrule', rrule)
                
                cal.add_component(ical_event)
            
            return cal.to_ical().decode('utf-8')
        except Exception as e:
            logger.error(f"Error exporting calendar to iCal: {e}")
            raise
    
    def _build_rrule(self, recurrence_type: RecurrenceType, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build RRULE for iCal export"""
        try:
            if recurrence_type == RecurrenceType.DAILY:
                return {'FREQ': 'DAILY'}
            elif recurrence_type == RecurrenceType.WEEKLY:
                return {'FREQ': 'WEEKLY'}
            elif recurrence_type == RecurrenceType.MONTHLY:
                return {'FREQ': 'MONTHLY'}
            elif recurrence_type == RecurrenceType.YEARLY:
                return {'FREQ': 'YEARLY'}
            return None
        except Exception as e:
            logger.error(f"Error building RRULE: {e}")
            return None
    
    # Statistics and Analytics
    def get_calendar_stats(self, user_id: Optional[int] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get calendar statistics"""
        try:
            query = self.db.query(CalendarEvent)
            
            if user_id:
                query = query.join(EventParticipant).filter(EventParticipant.user_id == user_id)
            
            if start_date:
                query = query.filter(CalendarEvent.start_date >= start_date)
            if end_date:
                query = query.filter(CalendarEvent.end_date <= end_date)
            
            total_events = query.count()
            
            # Events by type
            events_by_type = self.db.query(
                CalendarEvent.event_type,
                func.count(CalendarEvent.id).label('count')
            ).group_by(CalendarEvent.event_type).all()
            
            # Events by status
            events_by_status = self.db.query(
                CalendarEvent.status,
                func.count(CalendarEvent.id).label('count')
            ).group_by(CalendarEvent.status).all()
            
            # Upcoming events (next 7 days)
            upcoming_start = datetime.utcnow()
            upcoming_end = upcoming_start + timedelta(days=7)
            upcoming_events = query.filter(
                and_(
                    CalendarEvent.start_date >= upcoming_start,
                    CalendarEvent.start_date <= upcoming_end
                )
            ).count()
            
            return {
                "total_events": total_events,
                "events_by_type": {item.event_type: item.count for item in events_by_type},
                "events_by_status": {item.status: item.count for item in events_by_status},
                "upcoming_events": upcoming_events
            }
        except Exception as e:
            logger.error(f"Error getting calendar stats: {e}")
            raise
    
    # Search and Filter
    def search_events(self, search_term: str, user_id: Optional[int] = None, limit: int = 50) -> List[CalendarEvent]:
        """Search events by title, description, or location"""
        try:
            query = self.db.query(CalendarEvent).options(
                joinedload(CalendarEvent.category),
                joinedload(CalendarEvent.participants).joinedload(EventParticipant.user)
            )
            
            # Add search filters
            search_filter = or_(
                CalendarEvent.title.ilike(f"%{search_term}%"),
                CalendarEvent.description.ilike(f"%{search_term}%"),
                CalendarEvent.location.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)
            
            # Add user filter if specified
            if user_id:
                query = query.join(EventParticipant).filter(EventParticipant.user_id == user_id)
            
            return query.order_by(CalendarEvent.start_date).limit(limit).all()
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            raise 