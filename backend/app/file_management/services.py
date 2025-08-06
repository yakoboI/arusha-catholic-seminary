"""
File Management Services

Service layer for file upload, storage, and management operations.
"""

import os
import hashlib
import mimetypes
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
import structlog

from app.config import settings
from app.models import User
from .models import FileRecord, FileCategory, FileRecordCreate, FileRecordUpdate, FileSearchParams

logger = structlog.get_logger()


class FileService:
    """Service for file management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create category subdirectories
        for category in FileCategory:
            category_dir = self.upload_dir / category.value
            category_dir.mkdir(exist_ok=True)
    
    def upload_file(
        self, 
        file: UploadFile, 
        user: User, 
        category: FileCategory = FileCategory.OTHER,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        is_public: bool = False,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None
    ) -> FileRecord:
        """Upload a file and create file record"""
        
        # Validate file
        self._validate_file(file)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = self._get_file_extension(file.filename)
        unique_filename = f"{timestamp}_{user.id}_{file.filename}"
        
        # Create file path
        category_dir = self.upload_dir / category.value
        file_path = category_dir / unique_filename
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Calculate file size and checksum
            file_size = file_path.stat().st_size
            checksum = self._calculate_checksum(file_path)
            
            # Determine MIME type
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
            
            # Create file record
            file_record = FileRecord(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=str(file_path),
                file_size=file_size,
                mime_type=mime_type,
                file_extension=file_extension,
                category=category.value,
                description=description,
                tags=tags,
                uploaded_by=user.id,
                is_public=is_public,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                checksum=checksum
            )
            
            self.db.add(file_record)
            self.db.commit()
            self.db.refresh(file_record)
            
            logger.info(
                "File uploaded successfully",
                file_id=file_record.id,
                filename=file.filename,
                size=file_size,
                user_id=user.id
            )
            
            return file_record
            
        except Exception as e:
            # Clean up file if database operation fails
            if file_path.exists():
                file_path.unlink()
            
            logger.error(
                "File upload failed",
                filename=file.filename,
                error=str(e),
                user_id=user.id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file"
            )
    
    def get_file(self, file_id: int, user: User) -> FileRecord:
        """Get file record by ID with access control"""
        file_record = self.db.query(FileRecord).filter(
            and_(
                FileRecord.id == file_id,
                FileRecord.is_deleted == False
            )
        ).first()
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Check access permissions
        if not self._can_access_file(file_record, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return file_record
    
    def list_files(self, user: User, search_params: FileSearchParams) -> Tuple[List[FileRecord], int]:
        """List files with search and filtering"""
        query = self.db.query(FileRecord).filter(FileRecord.is_deleted == False)
        
        # Apply search filters
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    FileRecord.filename.ilike(search_term),
                    FileRecord.original_filename.ilike(search_term),
                    FileRecord.description.ilike(search_term)
                )
            )
        
        if search_params.category:
            query = query.filter(FileRecord.category == search_params.category.value)
        
        if search_params.uploaded_by:
            query = query.filter(FileRecord.uploaded_by == search_params.uploaded_by)
        
        if search_params.related_entity_type:
            query = query.filter(FileRecord.related_entity_type == search_params.related_entity_type)
        
        if search_params.related_entity_id:
            query = query.filter(FileRecord.related_entity_id == search_params.related_entity_id)
        
        if search_params.is_public is not None:
            query = query.filter(FileRecord.is_public == search_params.is_public)
        
        if search_params.date_from:
            query = query.filter(FileRecord.uploaded_at >= search_params.date_from)
        
        if search_params.date_to:
            query = query.filter(FileRecord.uploaded_at <= search_params.date_to)
        
        # Apply access control (non-admin users can only see their own files and public files)
        if user.role != "admin":
            query = query.filter(
                or_(
                    FileRecord.uploaded_by == user.id,
                    FileRecord.is_public == True
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if search_params.sort_order == "desc":
            query = query.order_by(desc(getattr(FileRecord, search_params.sort_by)))
        else:
            query = query.order_by(asc(getattr(FileRecord, search_params.sort_by)))
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.per_page
        files = query.offset(offset).limit(search_params.per_page).all()
        
        return files, total
    
    def update_file(self, file_id: int, update_data: FileRecordUpdate, user: User) -> FileRecord:
        """Update file record metadata"""
        file_record = self.get_file(file_id, user)
        
        # Check if user can modify the file
        if file_record.uploaded_by != user.id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify file"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(file_record, field, value)
        
        self.db.commit()
        self.db.refresh(file_record)
        
        logger.info(
            "File updated",
            file_id=file_id,
            user_id=user.id,
            updated_fields=list(update_dict.keys())
        )
        
        return file_record
    
    def delete_file(self, file_id: int, user: User) -> bool:
        """Soft delete file record"""
        file_record = self.get_file(file_id, user)
        
        # Check if user can delete the file
        if file_record.uploaded_by != user.id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete file"
            )
        
        # Soft delete
        file_record.is_deleted = True
        self.db.commit()
        
        logger.info(
            "File deleted",
            file_id=file_id,
            user_id=user.id
        )
        
        return True
    
    def get_file_path(self, file_record: FileRecord) -> Path:
        """Get physical file path"""
        file_path = Path(file_record.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        return file_path
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        # Check file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Check file extension
        file_extension = self._get_file_extension(file.filename)
        allowed_extensions = settings.ALLOWED_EXTENSIONS.split(",")
        
        if file_extension.lower() not in [ext.strip().lower() for ext in allowed_extensions]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        return Path(filename).suffix.lower()
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _can_access_file(self, file_record: FileRecord, user: User) -> bool:
        """Check if user can access file"""
        # Admin can access all files
        if user.role == "admin":
            return True
        
        # User can access their own files
        if file_record.uploaded_by == user.id:
            return True
        
        # User can access public files
        if file_record.is_public:
            return True
        
        return False
    
    def get_files_by_entity(self, entity_type: str, entity_id: int, user: User) -> List[FileRecord]:
        """Get files related to a specific entity"""
        query = self.db.query(FileRecord).filter(
            and_(
                FileRecord.related_entity_type == entity_type,
                FileRecord.related_entity_id == entity_id,
                FileRecord.is_deleted == False
            )
        )
        
        # Apply access control
        if user.role != "admin":
            query = query.filter(
                or_(
                    FileRecord.uploaded_by == user.id,
                    FileRecord.is_public == True
                )
            )
        
        return query.all()
    
    def get_storage_stats(self, user: User) -> dict:
        """Get file storage statistics"""
        query = self.db.query(FileRecord).filter(FileRecord.is_deleted == False)
        
        # Apply access control
        if user.role != "admin":
            query = query.filter(
                or_(
                    FileRecord.uploaded_by == user.id,
                    FileRecord.is_public == True
                )
            )
        
        total_files = query.count()
        total_size = query.with_entities(FileRecord.file_size).all()
        total_size = sum(size[0] for size in total_size) if total_size else 0
        
        # Files by category
        category_stats = {}
        for category in FileCategory:
            category_count = query.filter(FileRecord.category == category.value).count()
            if category_count > 0:
                category_stats[category.value] = category_count
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "category_stats": category_stats
        } 