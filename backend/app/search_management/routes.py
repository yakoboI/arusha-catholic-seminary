"""
Search Management Routes

This module defines the FastAPI routes for search functionality
including search, filtering, and analytics endpoints.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from .models import SearchRequest, SearchResponse, SearchStatistics, SearchIndexRequest
from .services import SearchService

router = APIRouter(prefix="/api/v1/search", tags=["Search Management"])


@router.post("/", response_model=SearchResponse)
async def search(
    search_request: SearchRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Perform advanced search with filtering and pagination
    
    - **query**: Search text to find
    - **entity_type**: Type of entity to search (student, teacher, class, grade, attendance)
    - **filters**: Additional filters to apply
    - **page**: Page number for pagination
    - **page_size**: Number of items per page
    - **sort_by**: Field to sort by
    - **sort_order**: Sort order (asc or desc)
    """
    try:
        search_service = SearchService(db)
        
        # Get client information
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Perform search
        result = await search_service.search(
            search_request=search_request,
            user_id=current_user.id if current_user else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/config/{entity_type}")
async def get_search_config(
    entity_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get search configuration for a specific entity type
    
    Returns available filters, sort options, and searchable fields
    """
    try:
        search_service = SearchService(db)
        config = await search_service.get_search_config(entity_type)
        
        if not config:
            raise HTTPException(status_code=404, detail=f"Entity type '{entity_type}' not found")
        
        return config
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get search config: {str(e)}")


@router.get("/config")
async def get_all_search_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get search configurations for all entity types
    """
    try:
        search_service = SearchService(db)
        configs = {}
        
        for entity_type in ["student", "teacher", "class", "grade", "attendance"]:
            config = await search_service.get_search_config(entity_type)
            if config:
                configs[entity_type] = config
        
        return configs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get search configs: {str(e)}")


@router.get("/statistics", response_model=SearchStatistics)
async def get_search_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get search statistics and analytics
    
    Returns search activity metrics, popular terms, and performance data
    """
    try:
        search_service = SearchService(db)
        stats = await search_service.get_search_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get search statistics: {str(e)}")


@router.post("/index/rebuild")
async def rebuild_search_index(
    entity_type: Optional[str] = Query(None, description="Entity type to rebuild index for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rebuild search index for entities
    
    - **entity_type**: Optional entity type to rebuild index for (rebuilds all if not specified)
    """
    try:
        search_service = SearchService(db)
        result = await search_service.rebuild_search_index(entity_type)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rebuild search index: {str(e)}")


@router.post("/index")
async def create_search_index(
    index_request: SearchIndexRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update search index for a specific entity
    
    - **entity_type**: Type of entity
    - **entity_id**: ID of the entity
    - **searchable_text**: Text content for searching
    - **metadata**: Additional metadata for the index
    """
    try:
        from .models import SearchIndex
        
        # Check if index already exists
        existing_index = db.query(SearchIndex).filter(
            SearchIndex.entity_type == index_request.entity_type,
            SearchIndex.entity_id == index_request.entity_id
        ).first()
        
        if existing_index:
            # Update existing index
            existing_index.searchable_text = index_request.searchable_text
            existing_index.metadata = index_request.metadata
            existing_index.updated_at = datetime.utcnow()
        else:
            # Create new index
            search_index = SearchIndex(
                entity_type=index_request.entity_type,
                entity_id=index_request.entity_id,
                searchable_text=index_request.searchable_text,
                metadata=index_request.metadata
            )
            db.add(search_index)
        
        db.commit()
        return {"message": "Search index created/updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create search index: {str(e)}")


@router.delete("/index/{entity_type}/{entity_id}")
async def delete_search_index(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete search index for a specific entity
    """
    try:
        from .models import SearchIndex
        
        index = db.query(SearchIndex).filter(
            SearchIndex.entity_type == entity_type,
            SearchIndex.entity_id == entity_id
        ).first()
        
        if not index:
            raise HTTPException(status_code=404, detail="Search index not found")
        
        db.delete(index)
        db.commit()
        
        return {"message": "Search index deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete search index: {str(e)}")


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="Partial search query"),
    entity_type: Optional[str] = Query(None, description="Entity type to get suggestions for"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get search suggestions based on partial query
    
    Returns autocomplete suggestions for search queries
    """
    try:
        from .models import SearchLog
        
        # Get recent search queries that match the partial query
        suggestions_query = db.query(SearchLog.query).filter(
            SearchLog.query.ilike(f"%{query}%"),
            SearchLog.query != query
        )
        
        if entity_type:
            suggestions_query = suggestions_query.filter(SearchLog.entity_type == entity_type)
        
        suggestions = suggestions_query.group_by(SearchLog.query).order_by(
            func.count(SearchLog.id).desc()
        ).limit(limit).all()
        
        return {
            "query": query,
            "entity_type": entity_type,
            "suggestions": [suggestion.query for suggestion in suggestions]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get search suggestions: {str(e)}")


@router.get("/popular")
async def get_popular_searches(
    entity_type: Optional[str] = Query(None, description="Entity type to get popular searches for"),
    days: int = Query(7, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of popular searches"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get popular search queries
    
    Returns most frequently used search queries
    """
    try:
        from .models import SearchLog
        from datetime import datetime, timedelta
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get popular searches
        popular_query = db.query(
            SearchLog.query,
            func.count(SearchLog.id).label("count")
        ).filter(
            SearchLog.created_at >= start_date,
            SearchLog.created_at <= end_date,
            SearchLog.query != ""
        )
        
        if entity_type:
            popular_query = popular_query.filter(SearchLog.entity_type == entity_type)
        
        popular_searches = popular_query.group_by(SearchLog.query).order_by(
            func.count(SearchLog.id).desc()
        ).limit(limit).all()
        
        return {
            "entity_type": entity_type,
            "days": days,
            "popular_searches": [
                {"query": search.query, "count": search.count}
                for search in popular_searches
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get popular searches: {str(e)}")


@router.get("/logs")
async def get_search_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get search logs for analytics and debugging
    
    Returns paginated search log entries with optional filtering
    """
    try:
        from .models import SearchLog
        
        query = db.query(SearchLog)
        
        if entity_type:
            query = query.filter(SearchLog.entity_type == entity_type)
        
        if user_id:
            query = query.filter(SearchLog.user_id == user_id)
        
        logs = query.order_by(SearchLog.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "query": log.query,
                    "entity_type": log.entity_type,
                    "filters": log.filters,
                    "result_count": log.result_count,
                    "search_time_ms": log.search_time_ms,
                    "user_id": log.user_id,
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get search logs: {str(e)}") 