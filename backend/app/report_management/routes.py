"""
Report Management Routes

This module defines FastAPI routes for report operations including
template management, report generation, and scheduling.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from .models import (
    ReportTemplate, ReportLog, ReportSchedule, ReportType, ReportFormat, ReportStatus,
    ReportTemplateCreate, ReportTemplateUpdate, ReportTemplateResponse,
    ReportGenerateRequest, ReportLogResponse, ReportScheduleCreate, ReportStats
)
from .services import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["Report Management"])


# Template Management Endpoints
@router.post("/templates", response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_report_template(
    template_data: ReportTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new report template"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can create report templates"
        )
    
    report_service = ReportService(db)
    template = report_service.create_template(template_data, current_user)
    return template


@router.get("/templates", response_model=List[ReportTemplateResponse])
async def list_report_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    report_type: Optional[ReportType] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List report templates with filtering and pagination"""
    report_service = ReportService(db)
    templates, total = report_service.list_templates(skip, limit, report_type, is_active)
    return templates


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
async def get_report_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get report template by ID"""
    report_service = ReportService(db)
    template = report_service.get_template(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found"
        )
    
    return template


@router.put("/templates/{template_id}", response_model=ReportTemplateResponse)
async def update_report_template(
    template_id: int,
    template_data: ReportTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update report template"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can update report templates"
        )
    
    report_service = ReportService(db)
    template = report_service.update_template(template_id, template_data)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found"
        )
    
    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete report template (soft delete)"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can delete report templates"
        )
    
    report_service = ReportService(db)
    success = report_service.delete_template(template_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found"
        )


# Report Generation Endpoints
@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_report(
    request: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a report"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can generate reports"
        )
    
    report_service = ReportService(db)
    success = await report_service.generate_report_async(request, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )
    
    return {"message": "Report generation started successfully"}


# Report Logs Endpoints
@router.get("/logs", response_model=List[ReportLogResponse])
async def get_report_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    report_type: Optional[ReportType] = Query(None),
    status: Optional[ReportStatus] = Query(None),
    output_format: Optional[ReportFormat] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get report logs with filtering and pagination"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can view report logs"
        )
    
    report_service = ReportService(db)
    logs, total = report_service.get_report_logs(
        skip, limit, report_type, status, output_format, start_date, end_date
    )
    return logs


@router.get("/logs/{log_id}", response_model=ReportLogResponse)
async def get_report_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific report log by ID"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can view report logs"
        )
    
    log = db.query(ReportLog).filter(ReportLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report log not found"
        )
    
    return log


@router.get("/logs/{log_id}/download")
async def download_report(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download generated report file"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can download reports"
        )
    
    log = db.query(ReportLog).filter(ReportLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report log not found"
        )
    
    if log.status != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report is not ready for download"
        )
    
    if not log.file_path or not log.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    # Return file for download
    return FileResponse(
        path=log.file_path,
        filename=f"{log.report_name}.{log.output_format}",
        media_type="application/octet-stream"
    )


# Report Statistics Endpoints
@router.get("/stats", response_model=ReportStats)
async def get_report_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get report statistics"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can view report statistics"
        )
    
    report_service = ReportService(db)
    stats = report_service.get_report_stats(days)
    return stats


# Report Types and Formats Endpoints
@router.get("/types", status_code=status.HTTP_200_OK)
async def get_report_types():
    """Get available report types"""
    return {
        "report_types": [
            {"value": report_type.value, "label": report_type.value.replace("_", " ").title()}
            for report_type in ReportType
        ]
    }


@router.get("/formats", status_code=status.HTTP_200_OK)
async def get_report_formats():
    """Get available report formats"""
    return {
        "report_formats": [
            {"value": format_type.value, "label": format_type.value.upper()}
            for format_type in ReportFormat
        ]
    }


@router.get("/statuses", status_code=status.HTTP_200_OK)
async def get_report_statuses():
    """Get available report statuses"""
    return {
        "report_statuses": [
            {"value": status.value, "label": status.value.replace("_", " ").title()}
            for status in ReportStatus
        ]
    }


# Quick Report Generation Endpoints
@router.post("/quick/student-list", status_code=status.HTTP_202_ACCEPTED)
async def generate_student_list_report(
    output_format: ReportFormat = ReportFormat.PDF,
    class_id: Optional[int] = Query(None),
    student_level: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick generate student list report"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can generate reports"
        )
    
    parameters = {}
    if class_id:
        parameters["class_id"] = class_id
    if student_level:
        parameters["student_level"] = student_level
    
    request = ReportGenerateRequest(
        report_type=ReportType.STUDENT_LIST,
        output_format=output_format,
        parameters=parameters
    )
    
    report_service = ReportService(db)
    success = await report_service.generate_report_async(request, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate student list report"
        )
    
    return {"message": "Student list report generation started successfully"}


@router.post("/quick/grade-report", status_code=status.HTTP_202_ACCEPTED)
async def generate_grade_report(
    output_format: ReportFormat = ReportFormat.PDF,
    class_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    academic_year: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick generate grade report"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can generate reports"
        )
    
    parameters = {}
    if class_id:
        parameters["class_id"] = class_id
    if subject_id:
        parameters["subject_id"] = subject_id
    if academic_year:
        parameters["academic_year"] = academic_year
    if semester:
        parameters["semester"] = semester
    
    request = ReportGenerateRequest(
        report_type=ReportType.GRADE_REPORT,
        output_format=output_format,
        parameters=parameters
    )
    
    report_service = ReportService(db)
    success = await report_service.generate_report_async(request, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate grade report"
        )
    
    return {"message": "Grade report generation started successfully"}


@router.post("/quick/attendance-report", status_code=status.HTTP_202_ACCEPTED)
async def generate_attendance_report(
    output_format: ReportFormat = ReportFormat.PDF,
    class_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick generate attendance report"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can generate reports"
        )
    
    parameters = {}
    if class_id:
        parameters["class_id"] = class_id
    if date_from:
        parameters["date_from"] = date_from
    if date_to:
        parameters["date_to"] = date_to
    
    request = ReportGenerateRequest(
        report_type=ReportType.ATTENDANCE_REPORT,
        output_format=output_format,
        parameters=parameters
    )
    
    report_service = ReportService(db)
    success = await report_service.generate_report_async(request, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate attendance report"
        )
    
    return {"message": "Attendance report generation started successfully"}


@router.post("/quick/financial-report", status_code=status.HTTP_202_ACCEPTED)
async def generate_financial_report(
    output_format: ReportFormat = ReportFormat.PDF,
    student_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick generate financial report"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and teachers can generate reports"
        )
    
    parameters = {}
    if student_id:
        parameters["student_id"] = student_id
    if date_from:
        parameters["date_from"] = date_from
    if date_to:
        parameters["date_to"] = date_to
    
    request = ReportGenerateRequest(
        report_type=ReportType.FINANCIAL_REPORT,
        output_format=output_format,
        parameters=parameters
    )
    
    report_service = ReportService(db)
    success = await report_service.generate_report_async(request, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate financial report"
        )
    
    return {"message": "Financial report generation started successfully"} 