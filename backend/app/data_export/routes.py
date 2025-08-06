"""
Data Export Routes

This module defines the FastAPI routes for data export functionality
including export jobs, templates, and file downloads.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from .models import ExportRequest, ExportResponse, ExportTemplateCreate, ExportTemplateResponse, ExportStatistics
from .services import DataExportService

router = APIRouter(prefix="/api/v1/export", tags=["Data Export"])


@router.post("/jobs", response_model=ExportResponse)
async def create_export_job(
    export_request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new export job
    
    - **name**: Export job name
    - **description**: Optional description
    - **entity_type**: Type of entity to export (student, teacher, class, grade, attendance)
    - **export_format**: Export format (csv, xlsx, pdf, json, xml)
    - **filters**: Optional filters to apply
    - **columns**: Selected columns to export
    - **template_id**: Optional export template ID
    """
    try:
        export_service = DataExportService(db)
        
        # Create export job
        job = await export_service.create_export_job(export_request, current_user.id)
        
        # Process job in background
        background_tasks.add_task(export_service.process_export_job, job.id)
        
        return ExportResponse(
            id=job.id,
            name=job.name,
            description=job.description,
            entity_type=job.entity_type,
            export_format=job.export_format,
            status=job.status,
            file_path=job.file_path,
            file_size=job.file_size,
            record_count=job.record_count,
            processing_time=job.processing_time,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export job creation failed: {str(e)}")


@router.get("/jobs", response_model=list[ExportResponse])
async def get_export_jobs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
    status: Optional[str] = Query(None, description="Filter by status"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get export jobs with optional filtering
    
    Returns paginated list of export jobs
    """
    try:
        export_service = DataExportService(db)
        jobs = await export_service.get_export_jobs(skip, limit, status)
        
        # Filter by entity type if specified
        if entity_type:
            jobs = [job for job in jobs if job.entity_type == entity_type]
        
        return [
            ExportResponse(
                id=job.id,
                name=job.name,
                description=job.description,
                entity_type=job.entity_type,
                export_format=job.export_format,
                status=job.status,
                file_path=job.file_path,
                file_size=job.file_size,
                record_count=job.record_count,
                processing_time=job.processing_time,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at
            )
            for job in jobs
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export jobs: {str(e)}")


@router.get("/jobs/{job_id}", response_model=ExportResponse)
async def get_export_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get export job by ID
    """
    try:
        export_service = DataExportService(db)
        job = await export_service.get_export_job_by_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Export job not found")
        
        return ExportResponse(
            id=job.id,
            name=job.name,
            description=job.description,
            entity_type=job.entity_type,
            export_format=job.export_format,
            status=job.status,
            file_path=job.file_path,
            file_size=job.file_size,
            record_count=job.record_count,
            processing_time=job.processing_time,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export job: {str(e)}")


@router.post("/jobs/{job_id}/cancel")
async def cancel_export_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an export job
    """
    try:
        export_service = DataExportService(db)
        success = await export_service.cancel_export_job(job_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Cannot cancel this export job")
        
        return {"message": "Export job cancelled successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel export job: {str(e)}")


@router.delete("/jobs/{job_id}")
async def delete_export_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an export job and its file
    """
    try:
        export_service = DataExportService(db)
        success = await export_service.delete_export_job(job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Export job not found")
        
        return {"message": "Export job deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete export job: {str(e)}")


@router.get("/jobs/{job_id}/download")
async def download_export_file(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download export file
    """
    try:
        export_service = DataExportService(db)
        job = await export_service.get_export_job_by_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Export job not found")
        
        if job.status != "completed":
            raise HTTPException(status_code=400, detail="Export job not completed")
        
        if not job.file_path:
            raise HTTPException(status_code=404, detail="Export file not found")
        
        # Return file for download
        return FileResponse(
            path=job.file_path,
            filename=f"{job.name}.{job.export_format}",
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download export file: {str(e)}")


@router.post("/templates", response_model=ExportTemplateResponse)
async def create_export_template(
    template_data: ExportTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new export template
    
    - **name**: Template name
    - **description**: Optional description
    - **entity_type**: Entity type for template
    - **export_format**: Export format
    - **columns**: Column configuration
    - **filters**: Default filters
    - **sorting**: Default sorting
    - **is_default**: Is default template
    """
    try:
        export_service = DataExportService(db)
        template = await export_service.create_export_template(template_data.dict(), current_user.id)
        
        return ExportTemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            entity_type=template.entity_type,
            export_format=template.export_format,
            columns=template.columns,
            filters=template.filters,
            sorting=template.sorting,
            is_active=template.is_active,
            is_default=template.is_default,
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create export template: {str(e)}")


@router.get("/templates", response_model=list[ExportTemplateResponse])
async def get_export_templates(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get export templates
    
    Returns list of export templates with optional filtering
    """
    try:
        export_service = DataExportService(db)
        templates = await export_service.get_export_templates(entity_type)
        
        return [
            ExportTemplateResponse(
                id=template.id,
                name=template.name,
                description=template.description,
                entity_type=template.entity_type,
                export_format=template.export_format,
                columns=template.columns,
                filters=template.filters,
                sorting=template.sorting,
                is_active=template.is_active,
                is_default=template.is_default,
                created_at=template.created_at,
                updated_at=template.updated_at
            )
            for template in templates
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export templates: {str(e)}")


@router.get("/templates/{template_id}", response_model=ExportTemplateResponse)
async def get_export_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get export template by ID
    """
    try:
        from .models import ExportTemplate
        
        template = db.query(ExportTemplate).filter(ExportTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Export template not found")
        
        return ExportTemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            entity_type=template.entity_type,
            export_format=template.export_format,
            columns=template.columns,
            filters=template.filters,
            sorting=template.sorting,
            is_active=template.is_active,
            is_default=template.is_default,
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export template: {str(e)}")


@router.put("/templates/{template_id}", response_model=ExportTemplateResponse)
async def update_export_template(
    template_id: int,
    template_update: ExportTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an export template
    """
    try:
        from .models import ExportTemplate
        
        template = db.query(ExportTemplate).filter(ExportTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Export template not found")
        
        # Update template fields
        for field, value in template_update.dict().items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(template)
        
        return ExportTemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            entity_type=template.entity_type,
            export_format=template.export_format,
            columns=template.columns,
            filters=template.filters,
            sorting=template.sorting,
            is_active=template.is_active,
            is_default=template.is_default,
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update export template: {str(e)}")


@router.delete("/templates/{template_id}")
async def delete_export_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an export template
    """
    try:
        from .models import ExportTemplate
        
        template = db.query(ExportTemplate).filter(ExportTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Export template not found")
        
        db.delete(template)
        db.commit()
        
        return {"message": "Export template deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete export template: {str(e)}")


@router.get("/config/{entity_type}")
async def get_export_config(
    entity_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get export configuration for entity type
    
    Returns available columns, formats, and limits
    """
    try:
        export_service = DataExportService(db)
        config = await export_service.get_export_config(entity_type)
        
        if not config:
            raise HTTPException(status_code=404, detail=f"Entity type '{entity_type}' not found")
        
        return config
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export config: {str(e)}")


@router.get("/config")
async def get_all_export_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get export configurations for all entity types
    """
    try:
        export_service = DataExportService(db)
        configs = {}
        
        for entity_type in ["student", "teacher", "class", "grade", "attendance"]:
            config = await export_service.get_export_config(entity_type)
            if config:
                configs[entity_type] = config
        
        return configs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export configs: {str(e)}")


@router.get("/statistics", response_model=ExportStatistics)
async def get_export_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get export statistics and analytics
    
    Returns export activity metrics and performance data
    """
    try:
        export_service = DataExportService(db)
        stats = await export_service.get_export_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export statistics: {str(e)}")


@router.post("/quick/{entity_type}")
async def quick_export(
    entity_type: str,
    export_format: str = Query(..., description="Export format"),
    columns: Optional[str] = Query(None, description="Comma-separated column names"),
    filters: Optional[str] = Query(None, description="JSON string of filters"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Quick export without creating a job
    
    - **entity_type**: Entity type to export
    - **export_format**: Export format
    - **columns**: Comma-separated column names
    - **filters**: JSON string of filters
    """
    try:
        import json
        
        # Parse columns and filters
        column_list = columns.split(",") if columns else None
        filter_dict = json.loads(filters) if filters else None
        
        # Create export request
        export_request = ExportRequest(
            name=f"Quick Export - {entity_type}",
            entity_type=entity_type,
            export_format=export_format,
            columns=column_list,
            filters=filter_dict
        )
        
        export_service = DataExportService(db)
        
        # Create and process job immediately
        job = await export_service.create_export_job(export_request, current_user.id)
        job = await export_service.process_export_job(job.id)
        
        if job.status == "completed":
            return {
                "message": "Export completed successfully",
                "job_id": job.id,
                "file_path": job.file_path,
                "record_count": job.record_count,
                "file_size": job.file_size
            }
        else:
            raise HTTPException(status_code=500, detail=f"Export failed: {job.error_message}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick export failed: {str(e)}") 