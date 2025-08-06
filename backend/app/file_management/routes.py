"""
File Management Routes

API routes for file upload, download, and management operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import structlog

from app.database import get_db
from app.auth import get_current_user
from app.models import User
from .models import (
    FileRecord, FileCategory, FileRecordResponse, FileUploadResponse, 
    FileListResponse, FileRecordUpdate, FileSearchParams
)
from .services import FileService

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    category: FileCategory = Form(FileCategory.OTHER),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    is_public: bool = Form(False),
    related_entity_type: Optional[str] = Form(None),
    related_entity_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new file"""
    file_service = FileService(db)
    
    try:
        file_record = file_service.upload_file(
            file=file,
            user=current_user,
            category=category,
            description=description,
            tags=tags,
            is_public=is_public,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )
        
        # Get uploader name
        uploader_name = current_user.full_name or current_user.username
        
        # Create response
        file_response = FileRecordResponse(
            id=file_record.id,
            filename=file_record.filename,
            original_filename=file_record.original_filename,
            file_size=file_record.file_size,
            mime_type=file_record.mime_type,
            file_extension=file_record.file_extension,
            category=FileCategory(file_record.category),
            description=file_record.description,
            tags=file_record.tags,
            uploaded_by=file_record.uploaded_by,
            uploaded_at=file_record.uploaded_at,
            is_public=file_record.is_public,
            is_deleted=file_record.is_deleted,
            related_entity_type=file_record.related_entity_type,
            related_entity_id=file_record.related_entity_id,
            is_processed=file_record.is_processed,
            processing_status=file_record.processing_status,
            virus_scan_status=file_record.virus_scan_status,
            checksum=file_record.checksum,
            uploader_name=uploader_name
        )
        
        download_url = f"/api/v1/files/{file_record.id}/download"
        preview_url = f"/api/v1/files/{file_record.id}/preview" if file_record.mime_type.startswith(('image/', 'text/', 'application/pdf')) else None
        
        return FileUploadResponse(
            file_record=file_response,
            download_url=download_url,
            preview_url=preview_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("File upload failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )


@router.get("/", response_model=FileListResponse)
async def list_files(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[FileCategory] = Query(None, description="File category"),
    uploaded_by: Optional[int] = Query(None, description="Uploader ID"),
    related_entity_type: Optional[str] = Query(None, description="Related entity type"),
    related_entity_id: Optional[int] = Query(None, description="Related entity ID"),
    is_public: Optional[bool] = Query(None, description="Public files only"),
    date_from: Optional[str] = Query(None, description="Upload date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Upload date to (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("uploaded_at", regex="^(filename|file_size|uploaded_at|category)$", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List files with search and filtering"""
    file_service = FileService(db)
    
    # Parse date parameters
    from datetime import datetime
    parsed_date_from = None
    parsed_date_to = None
    
    if date_from:
        try:
            parsed_date_from = datetime.strptime(date_from, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use YYYY-MM-DD"
            )
    
    if date_to:
        try:
            parsed_date_to = datetime.strptime(date_to, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use YYYY-MM-DD"
            )
    
    # Create search parameters
    search_params = FileSearchParams(
        query=query,
        category=category,
        uploaded_by=uploaded_by,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        is_public=is_public,
        date_from=parsed_date_from,
        date_to=parsed_date_to,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    try:
        files, total = file_service.list_files(current_user, search_params)
        
        # Convert to response models
        file_responses = []
        for file_record in files:
            uploader_name = None
            if file_record.uploader:
                uploader_name = file_record.uploader.full_name or file_record.uploader.username
            
            file_response = FileRecordResponse(
                id=file_record.id,
                filename=file_record.filename,
                original_filename=file_record.original_filename,
                file_size=file_record.file_size,
                mime_type=file_record.mime_type,
                file_extension=file_record.file_extension,
                category=FileCategory(file_record.category),
                description=file_record.description,
                tags=file_record.tags,
                uploaded_by=file_record.uploaded_by,
                uploaded_at=file_record.uploaded_at,
                is_public=file_record.is_public,
                is_deleted=file_record.is_deleted,
                related_entity_type=file_record.related_entity_type,
                related_entity_id=file_record.related_entity_id,
                is_processed=file_record.is_processed,
                processing_status=file_record.processing_status,
                virus_scan_status=file_record.virus_scan_status,
                checksum=file_record.checksum,
                uploader_name=uploader_name
            )
            file_responses.append(file_response)
        
        total_pages = (total + per_page - 1) // per_page
        
        return FileListResponse(
            files=file_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error("Failed to list files", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files"
        )


@router.get("/{file_id}", response_model=FileRecordResponse)
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file record by ID"""
    file_service = FileService(db)
    
    try:
        file_record = file_service.get_file(file_id, current_user)
        
        # Get uploader name
        uploader_name = None
        if file_record.uploader:
            uploader_name = file_record.uploader.full_name or file_record.uploader.username
        
        return FileRecordResponse(
            id=file_record.id,
            filename=file_record.filename,
            original_filename=file_record.original_filename,
            file_size=file_record.file_size,
            mime_type=file_record.mime_type,
            file_extension=file_record.file_extension,
            category=FileCategory(file_record.category),
            description=file_record.description,
            tags=file_record.tags,
            uploaded_by=file_record.uploaded_by,
            uploaded_at=file_record.uploaded_at,
            is_public=file_record.is_public,
            is_deleted=file_record.is_deleted,
            related_entity_type=file_record.related_entity_type,
            related_entity_id=file_record.related_entity_id,
            is_processed=file_record.is_processed,
            processing_status=file_record.processing_status,
            virus_scan_status=file_record.virus_scan_status,
            checksum=file_record.checksum,
            uploader_name=uploader_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get file", file_id=file_id, error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get file"
        )


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download file"""
    file_service = FileService(db)
    
    try:
        file_record = file_service.get_file(file_id, current_user)
        file_path = file_service.get_file_path(file_record)
        
        return FileResponse(
            path=file_path,
            filename=file_record.original_filename,
            media_type=file_record.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to download file", file_id=file_id, error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download file"
        )


@router.get("/{file_id}/preview")
async def preview_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview file (for images, PDFs, and text files)"""
    file_service = FileService(db)
    
    try:
        file_record = file_service.get_file(file_id, current_user)
        
        # Check if file can be previewed
        if not file_record.mime_type.startswith(('image/', 'text/', 'application/pdf')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not supported for preview"
            )
        
        file_path = file_service.get_file_path(file_record)
        
        return FileResponse(
            path=file_path,
            media_type=file_record.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to preview file", file_id=file_id, error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preview file"
        )


@router.put("/{file_id}", response_model=FileRecordResponse)
async def update_file(
    file_id: int,
    update_data: FileRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update file metadata"""
    file_service = FileService(db)
    
    try:
        file_record = file_service.update_file(file_id, update_data, current_user)
        
        # Get uploader name
        uploader_name = None
        if file_record.uploader:
            uploader_name = file_record.uploader.full_name or file_record.uploader.username
        
        return FileRecordResponse(
            id=file_record.id,
            filename=file_record.filename,
            original_filename=file_record.original_filename,
            file_size=file_record.file_size,
            mime_type=file_record.mime_type,
            file_extension=file_record.file_extension,
            category=FileCategory(file_record.category),
            description=file_record.description,
            tags=file_record.tags,
            uploaded_by=file_record.uploaded_by,
            uploaded_at=file_record.uploaded_at,
            is_public=file_record.is_public,
            is_deleted=file_record.is_deleted,
            related_entity_type=file_record.related_entity_type,
            related_entity_id=file_record.related_entity_id,
            is_processed=file_record.is_processed,
            processing_status=file_record.processing_status,
            virus_scan_status=file_record.virus_scan_status,
            checksum=file_record.checksum,
            uploader_name=uploader_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update file", file_id=file_id, error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update file"
        )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete file (soft delete)"""
    file_service = FileService(db)
    
    try:
        file_service.delete_file(file_id, current_user)
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete file", file_id=file_id, error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )


@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_files(
    entity_type: str,
    entity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get files related to a specific entity"""
    file_service = FileService(db)
    
    try:
        files = file_service.get_files_by_entity(entity_type, entity_id, current_user)
        
        # Convert to response models
        file_responses = []
        for file_record in files:
            uploader_name = None
            if file_record.uploader:
                uploader_name = file_record.uploader.full_name or file_record.uploader.username
            
            file_response = FileRecordResponse(
                id=file_record.id,
                filename=file_record.filename,
                original_filename=file_record.original_filename,
                file_size=file_record.file_size,
                mime_type=file_record.mime_type,
                file_extension=file_record.file_extension,
                category=FileCategory(file_record.category),
                description=file_record.description,
                tags=file_record.tags,
                uploaded_by=file_record.uploaded_by,
                uploaded_at=file_record.uploaded_at,
                is_public=file_record.is_public,
                is_deleted=file_record.is_deleted,
                related_entity_type=file_record.related_entity_type,
                related_entity_id=file_record.related_entity_id,
                is_processed=file_record.is_processed,
                processing_status=file_record.processing_status,
                virus_scan_status=file_record.virus_scan_status,
                checksum=file_record.checksum,
                uploader_name=uploader_name
            )
            file_responses.append(file_response)
        
        return {"files": file_responses, "total": len(file_responses)}
        
    except Exception as e:
        logger.error("Failed to get entity files", entity_type=entity_type, entity_id=entity_id, error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get entity files"
        )


@router.get("/stats/storage")
async def get_storage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file storage statistics"""
    file_service = FileService(db)
    
    try:
        stats = file_service.get_storage_stats(current_user)
        return stats
        
    except Exception as e:
        logger.error("Failed to get storage stats", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get storage stats"
        )


@router.get("/categories/list")
async def list_categories():
    """List available file categories"""
    return {
        "categories": [
            {"value": category.value, "label": category.value.replace("_", " ").title()}
            for category in FileCategory
        ]
    } 