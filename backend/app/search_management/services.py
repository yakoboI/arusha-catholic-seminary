"""
Search Management Services

This module provides comprehensive search and filtering capabilities
for the Arusha Catholic Seminary School Management System.
"""

import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc, text
from sqlalchemy.sql import extract

from ..models import User, Student, Teacher, Class, Grade, Attendance
from .models import SearchIndex, SearchLog, SearchRequest, SearchResponse, SearchStatistics


class SearchService:
    """Service class for advanced search and filtering"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Search configurations for different entities
        self.entity_configs = {
            "student": {
                "model": Student,
                "searchable_fields": ["first_name", "last_name", "email", "phone", "parent_name"],
                "filters": {
                    "class_id": {"type": "select", "field": "class_id"},
                    "status": {"type": "select", "field": "status"},
                    "admission_date_from": {"type": "date", "field": "admission_date"},
                    "admission_date_to": {"type": "date", "field": "admission_date"}
                },
                "sort_options": ["name", "email", "admission_date", "status"],
                "default_sort": "name"
            },
            "teacher": {
                "model": Teacher,
                "searchable_fields": ["first_name", "last_name", "email", "phone", "subject"],
                "filters": {
                    "subject": {"type": "select", "field": "subject"},
                    "status": {"type": "select", "field": "status"},
                    "hire_date_from": {"type": "date", "field": "hire_date"},
                    "hire_date_to": {"type": "date", "field": "hire_date"}
                },
                "sort_options": ["name", "email", "subject", "hire_date"],
                "default_sort": "name"
            },
            "class": {
                "model": Class,
                "searchable_fields": ["name", "grade_level"],
                "filters": {
                    "grade_level": {"type": "select", "field": "grade_level"},
                    "capacity_min": {"type": "number", "field": "capacity"},
                    "capacity_max": {"type": "number", "field": "capacity"}
                },
                "sort_options": ["name", "grade_level", "capacity"],
                "default_sort": "name"
            },
            "grade": {
                "model": Grade,
                "searchable_fields": ["subject", "comments"],
                "filters": {
                    "subject": {"type": "select", "field": "subject"},
                    "student_id": {"type": "select", "field": "student_id"},
                    "class_id": {"type": "select", "field": "student_id"},
                    "date_from": {"type": "date", "field": "date"},
                    "date_to": {"type": "date", "field": "date"},
                    "score_min": {"type": "number", "field": "score"},
                    "score_max": {"type": "number", "field": "score"}
                },
                "sort_options": ["date", "subject", "score", "student_name"],
                "default_sort": "date"
            },
            "attendance": {
                "model": Attendance,
                "searchable_fields": ["notes"],
                "filters": {
                    "status": {"type": "select", "field": "status"},
                    "user_id": {"type": "select", "field": "user_id"},
                    "date_from": {"type": "date", "field": "date"},
                    "date_to": {"type": "date", "field": "date"}
                },
                "sort_options": ["date", "status", "user_name"],
                "default_sort": "date"
            }
        }
    
    async def search(self, search_request: SearchRequest, user_id: Optional[int] = None, 
                    ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> SearchResponse:
        """Perform advanced search with filtering and pagination"""
        start_time = time.time()
        
        # Build search query
        query = self.db.query(self._get_model(search_request.entity_type))
        
        # Apply text search
        if search_request.query:
            query = self._apply_text_search(query, search_request.query, search_request.entity_type)
        
        # Apply filters
        if search_request.filters:
            query = self._apply_filters(query, search_request.filters, search_request.entity_type)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting
        query = self._apply_sorting(query, search_request.sort_by, search_request.sort_order, search_request.entity_type)
        
        # Apply pagination
        offset = (search_request.page - 1) * search_request.page_size
        results = query.offset(offset).limit(search_request.page_size).all()
        
        # Calculate search time
        search_time_ms = int((time.time() - start_time) * 1000)
        
        # Log search activity
        await self._log_search(search_request, total_count, search_time_ms, user_id, ip_address, user_agent)
        
        # Format results
        formatted_results = self._format_results(results, search_request.entity_type)
        
        return SearchResponse(
            query=search_request.query,
            entity_type=search_request.entity_type,
            results=formatted_results,
            total_count=total_count,
            page=search_request.page,
            page_size=search_request.page_size,
            total_pages=(total_count + search_request.page_size - 1) // search_request.page_size,
            search_time_ms=search_time_ms,
            filters_applied=search_request.filters or {}
        )
    
    def _get_model(self, entity_type: Optional[str]):
        """Get SQLAlchemy model for entity type"""
        if not entity_type:
            # Return a union of all models for global search
            return None
        
        config = self.entity_configs.get(entity_type)
        if not config:
            raise ValueError(f"Unsupported entity type: {entity_type}")
        
        return config["model"]
    
    def _apply_text_search(self, query, search_text: str, entity_type: Optional[str]) -> Any:
        """Apply full-text search to query"""
        if not search_text:
            return query
        
        # Split search terms
        search_terms = re.findall(r'\b\w+\b', search_text.lower())
        
        if not entity_type:
            # Global search across all entities
            return self._global_search(search_terms)
        
        config = self.entity_configs.get(entity_type)
        if not config:
            return query
        
        # Build search conditions
        search_conditions = []
        
        for term in search_terms:
            term_conditions = []
            
            for field in config["searchable_fields"]:
                if hasattr(config["model"], field):
                    term_conditions.append(
                        func.lower(getattr(config["model"], field)).contains(term)
                    )
            
            if term_conditions:
                search_conditions.append(or_(*term_conditions))
        
        if search_conditions:
            query = query.filter(and_(*search_conditions))
        
        return query
    
    def _global_search(self, search_terms: List[str]) -> Any:
        """Perform global search across all entities"""
        all_results = []
        
        for entity_type, config in self.entity_configs.items():
            model = config["model"]
            query = self.db.query(model)
            
            # Apply search to each entity type
            search_conditions = []
            for term in search_terms:
                term_conditions = []
                for field in config["searchable_fields"]:
                    if hasattr(model, field):
                        term_conditions.append(
                            func.lower(getattr(model, field)).contains(term)
                        )
                if term_conditions:
                    search_conditions.append(or_(*term_conditions))
            
            if search_conditions:
                query = query.filter(and_(*search_conditions))
                results = query.limit(10).all()  # Limit per entity type
                all_results.extend([{"entity_type": entity_type, "data": result} for result in results])
        
        return all_results
    
    def _apply_filters(self, query, filters: Dict[str, Any], entity_type: str) -> Any:
        """Apply filters to query"""
        if not filters or not entity_type:
            return query
        
        config = self.entity_configs.get(entity_type)
        if not config:
            return query
        
        filter_conditions = []
        
        for filter_key, filter_value in filters.items():
            if filter_value is None or filter_value == "":
                continue
            
            filter_config = config["filters"].get(filter_key)
            if not filter_config:
                continue
            
            field_name = filter_config["field"]
            filter_type = filter_config["type"]
            
            if not hasattr(config["model"], field_name):
                continue
            
            field = getattr(config["model"], field_name)
            
            if filter_type == "select":
                if isinstance(filter_value, list):
                    filter_conditions.append(field.in_(filter_value))
                else:
                    filter_conditions.append(field == filter_value)
            
            elif filter_type == "date":
                if filter_key.endswith("_from"):
                    filter_conditions.append(field >= filter_value)
                elif filter_key.endswith("_to"):
                    filter_conditions.append(field <= filter_value)
                else:
                    filter_conditions.append(field == filter_value)
            
            elif filter_type == "number":
                if filter_key.endswith("_min"):
                    filter_conditions.append(field >= filter_value)
                elif filter_key.endswith("_max"):
                    filter_conditions.append(field <= filter_value)
                else:
                    filter_conditions.append(field == filter_value)
            
            elif filter_type == "boolean":
                filter_conditions.append(field == bool(filter_value))
        
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))
        
        return query
    
    def _apply_sorting(self, query, sort_by: Optional[str], sort_order: str, entity_type: str) -> Any:
        """Apply sorting to query"""
        if not sort_by or not entity_type:
            return query
        
        config = self.entity_configs.get(entity_type)
        if not config or sort_by not in config["sort_options"]:
            return query
        
        if hasattr(config["model"], sort_by):
            field = getattr(config["model"], sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(field))
            else:
                query = query.order_by(asc(field))
        
        return query
    
    def _format_results(self, results: List[Any], entity_type: Optional[str]) -> List[Dict[str, Any]]:
        """Format search results for API response"""
        if not entity_type:
            # Global search results
            formatted = []
            for result in results:
                entity_data = self._format_entity_result(result["data"], result["entity_type"])
                entity_data["entity_type"] = result["entity_type"]
                formatted.append(entity_data)
            return formatted
        
        return [self._format_entity_result(result, entity_type) for result in results]
    
    def _format_entity_result(self, result: Any, entity_type: str) -> Dict[str, Any]:
        """Format individual entity result"""
        if entity_type == "student":
            return {
                "id": result.id,
                "name": f"{result.user.first_name} {result.user.last_name}",
                "email": result.user.email,
                "phone": result.user.phone,
                "class": result.class_.name if result.class_ else "Unassigned",
                "status": result.status,
                "admission_date": result.admission_date.isoformat() if result.admission_date else None,
                "parent_name": result.parent_name,
                "parent_phone": result.parent_phone
            }
        
        elif entity_type == "teacher":
            return {
                "id": result.id,
                "name": f"{result.user.first_name} {result.user.last_name}",
                "email": result.user.email,
                "phone": result.user.phone,
                "subject": result.subject,
                "qualification": result.qualification,
                "hire_date": result.hire_date.isoformat() if result.hire_date else None,
                "status": result.status
            }
        
        elif entity_type == "class":
            return {
                "id": result.id,
                "name": result.name,
                "grade_level": result.grade_level,
                "capacity": result.capacity,
                "current_enrollment": len(result.students),
                "teacher": f"{result.teacher.user.first_name} {result.teacher.user.last_name}" if result.teacher else "Unassigned"
            }
        
        elif entity_type == "grade":
            return {
                "id": result.id,
                "student_name": f"{result.student.user.first_name} {result.student.user.last_name}",
                "class": result.student.class_.name if result.student.class_ else "Unassigned",
                "subject": result.subject,
                "score": result.score,
                "max_score": result.max_score,
                "percentage": round((result.score / result.max_score) * 100, 2),
                "date": result.date.isoformat(),
                "comments": result.comments
            }
        
        elif entity_type == "attendance":
            return {
                "id": result.id,
                "student_name": f"{result.user.first_name} {result.user.last_name}",
                "class": result.user.student_profile.class_.name if result.user.student_profile and result.user.student_profile.class_ else "Unassigned",
                "date": result.date.isoformat(),
                "status": result.status,
                "time_in": result.time_in.isoformat() if result.time_in else None,
                "time_out": result.time_out.isoformat() if result.time_out else None,
                "notes": result.notes
            }
        
        # Default formatting
        return {c.name: getattr(result, c.name) for c in result.__table__.columns}
    
    async def _log_search(self, search_request: SearchRequest, result_count: int, 
                         search_time_ms: int, user_id: Optional[int] = None,
                         ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log search activity"""
        search_log = SearchLog(
            query=search_request.query,
            entity_type=search_request.entity_type,
            filters=search_request.filters,
            result_count=result_count,
            search_time_ms=search_time_ms,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(search_log)
        self.db.commit()
    
    async def get_search_statistics(self) -> SearchStatistics:
        """Get search statistics and analytics"""
        now = datetime.utcnow()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Basic counts
        total_searches = self.db.query(SearchLog).count()
        searches_today = self.db.query(SearchLog).filter(
            func.date(SearchLog.created_at) == today
        ).count()
        searches_this_week = self.db.query(SearchLog).filter(
            SearchLog.created_at >= week_ago
        ).count()
        searches_this_month = self.db.query(SearchLog).filter(
            SearchLog.created_at >= month_ago
        ).count()
        
        # Average search time
        avg_search_time = self.db.query(func.avg(SearchLog.search_time_ms)).scalar() or 0
        
        # Most searched terms
        most_searched_terms = self.db.query(
            SearchLog.query,
            func.count(SearchLog.id).label("count")
        ).filter(
            SearchLog.query != ""
        ).group_by(SearchLog.query).order_by(
            desc("count")
        ).limit(10).all()
        
        # Entity type distribution
        entity_distribution = self.db.query(
            SearchLog.entity_type,
            func.count(SearchLog.id).label("count")
        ).filter(
            SearchLog.entity_type.isnot(None)
        ).group_by(SearchLog.entity_type).all()
        
        # User search activity
        user_activity = self.db.query(
            SearchLog.user_id,
            func.count(SearchLog.id).label("count")
        ).filter(
            SearchLog.user_id.isnot(None)
        ).group_by(SearchLog.user_id).order_by(
            desc("count")
        ).limit(10).all()
        
        return SearchStatistics(
            total_searches=total_searches,
            searches_today=searches_today,
            searches_this_week=searches_this_week,
            searches_this_month=searches_this_month,
            average_search_time_ms=float(avg_search_time),
            most_searched_terms=[{"term": term.query, "count": term.count} for term in most_searched_terms],
            entity_type_distribution={dist.entity_type: dist.count for dist in entity_distribution},
            user_search_activity={str(activity.user_id): activity.count for activity in user_activity}
        )
    
    async def get_search_config(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """Get search configuration for entity type"""
        config = self.entity_configs.get(entity_type)
        if not config:
            return None
        
        # Build filter options
        filter_options = []
        for filter_key, filter_config in config["filters"].items():
            filter_option = {
                "field": filter_key,
                "label": filter_key.replace("_", " ").title(),
                "type": filter_config["type"]
            }
            
            # Add options for select filters
            if filter_config["type"] == "select":
                if filter_config["field"] == "status":
                    filter_option["options"] = ["active", "inactive", "suspended"]
                elif filter_config["field"] == "subject":
                    filter_option["options"] = ["Mathematics", "Science", "English", "History", "Geography"]
                elif filter_config["field"] == "grade_level":
                    filter_option["options"] = ["Form 1", "Form 2", "Form 3", "Form 4", "Form 5", "Form 6"]
            
            filter_options.append(filter_option)
        
        return {
            "entity_type": entity_type,
            "searchable_fields": config["searchable_fields"],
            "filters": filter_options,
            "sort_options": config["sort_options"],
            "default_sort": config["default_sort"],
            "page_size_options": [10, 20, 50, 100]
        }
    
    async def rebuild_search_index(self, entity_type: Optional[str] = None) -> Dict[str, Any]:
        """Rebuild search index for entities"""
        start_time = time.time()
        indexed_count = 0
        
        if entity_type:
            # Rebuild index for specific entity type
            indexed_count = await self._rebuild_entity_index(entity_type)
        else:
            # Rebuild index for all entity types
            for entity_type in self.entity_configs.keys():
                indexed_count += await self._rebuild_entity_index(entity_type)
        
        rebuild_time = int((time.time() - start_time) * 1000)
        
        return {
            "entity_type": entity_type or "all",
            "indexed_count": indexed_count,
            "rebuild_time_ms": rebuild_time
        }
    
    async def _rebuild_entity_index(self, entity_type: str) -> int:
        """Rebuild search index for specific entity type"""
        config = self.entity_configs.get(entity_type)
        if not config:
            return 0
        
        # Clear existing indices for this entity type
        self.db.query(SearchIndex).filter(
            SearchIndex.entity_type == entity_type
        ).delete()
        
        # Get all entities
        entities = self.db.query(config["model"]).all()
        indexed_count = 0
        
        for entity in entities:
            # Build searchable text
            searchable_text = self._build_searchable_text(entity, config["searchable_fields"])
            
            # Create search index
            search_index = SearchIndex(
                entity_type=entity_type,
                entity_id=entity.id,
                searchable_text=searchable_text,
                metadata=self._build_metadata(entity, entity_type)
            )
            
            self.db.add(search_index)
            indexed_count += 1
        
        self.db.commit()
        return indexed_count
    
    def _build_searchable_text(self, entity: Any, searchable_fields: List[str]) -> str:
        """Build searchable text from entity fields"""
        text_parts = []
        
        for field in searchable_fields:
            if hasattr(entity, field):
                value = getattr(entity, field)
                if value:
                    text_parts.append(str(value))
        
        # Add related entity text
        if hasattr(entity, 'user'):
            user = entity.user
            text_parts.extend([user.first_name, user.last_name, user.email])
        
        return " ".join(text_parts).lower()
    
    def _build_metadata(self, entity: Any, entity_type: str) -> Dict[str, Any]:
        """Build metadata for search index"""
        metadata = {"entity_type": entity_type}
        
        if entity_type == "student":
            metadata.update({
                "class_name": entity.class_.name if entity.class_ else None,
                "status": entity.status
            })
        elif entity_type == "teacher":
            metadata.update({
                "subject": entity.subject,
                "status": entity.status
            })
        elif entity_type == "class":
            metadata.update({
                "grade_level": entity.grade_level,
                "capacity": entity.capacity
            })
        
        return metadata 