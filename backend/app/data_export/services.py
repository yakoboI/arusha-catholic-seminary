"""
Data Export Services

This module provides comprehensive data export capabilities
for the Arusha Catholic Seminary School Management System.
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..models import User, Student, Teacher, Class, Grade, Attendance
from .models import (
    ExportJob, ExportTemplate, ExportFormat, ExportStatus,
    ExportRequest, ExportResponse, ExportStatistics
)


class DataExportService:
    """Service class for data export functionality"""
    
    def __init__(self, db: Session):
        self.db = db
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)
        
        # Export configurations for different entities
        self.entity_configs = {
            "student": {
                "model": Student,
                "available_columns": [
                    {"field": "id", "label": "ID", "type": "number"},
                    {"field": "student_id", "label": "Student ID", "type": "text"},
                    {"field": "admission_number", "label": "Admission Number", "type": "text"},
                    {"field": "full_name", "label": "Full Name", "type": "text"},
                    {"field": "date_of_birth", "label": "Date of Birth", "type": "date"},
                    {"field": "gender", "label": "Gender", "type": "text"},
                    {"field": "address", "label": "Address", "type": "text"},
                    {"field": "phone", "label": "Phone", "type": "text"},
                    {"field": "parent_name", "label": "Parent Name", "type": "text"},
                    {"field": "parent_phone", "label": "Parent Phone", "type": "text"},
                    {"field": "admission_date", "label": "Admission Date", "type": "date"},
                    {"field": "class_name", "label": "Class", "type": "text"},
                    {"field": "student_level", "label": "Level", "type": "text"},
                    {"field": "status", "label": "Status", "type": "text"}
                ],
                "default_columns": ["student_id", "full_name", "class_name", "status"],
                "supported_formats": ["csv", "xlsx", "pdf", "json"],
                "max_records": 10000,
                "batch_size": 1000
            },
            "teacher": {
                "model": Teacher,
                "available_columns": [
                    {"field": "id", "label": "ID", "type": "number"},
                    {"field": "employee_id", "label": "Employee ID", "type": "text"},
                    {"field": "full_name", "label": "Full Name", "type": "text"},
                    {"field": "department", "label": "Department", "type": "text"},
                    {"field": "qualification", "label": "Qualification", "type": "text"},
                    {"field": "hire_date", "label": "Hire Date", "type": "date"},
                    {"field": "phone", "label": "Phone", "type": "text"},
                    {"field": "address", "label": "Address", "type": "text"},
                    {"field": "status", "label": "Status", "type": "text"}
                ],
                "default_columns": ["employee_id", "full_name", "department", "status"],
                "supported_formats": ["csv", "xlsx", "pdf", "json"],
                "max_records": 5000,
                "batch_size": 500
            },
            "class": {
                "model": Class,
                "available_columns": [
                    {"field": "id", "label": "ID", "type": "number"},
                    {"field": "name", "label": "Class Name", "type": "text"},
                    {"field": "grade_level", "label": "Grade Level", "type": "text"},
                    {"field": "capacity", "label": "Capacity", "type": "number"},
                    {"field": "current_enrollment", "label": "Current Enrollment", "type": "number"},
                    {"field": "teacher_name", "label": "Teacher", "type": "text"},
                    {"field": "academic_year", "label": "Academic Year", "type": "text"},
                    {"field": "is_active", "label": "Active", "type": "boolean"}
                ],
                "default_columns": ["name", "grade_level", "capacity", "current_enrollment"],
                "supported_formats": ["csv", "xlsx", "pdf", "json"],
                "max_records": 1000,
                "batch_size": 100
            },
            "grade": {
                "model": Grade,
                "available_columns": [
                    {"field": "id", "label": "ID", "type": "number"},
                    {"field": "student_name", "label": "Student Name", "type": "text"},
                    {"field": "class_name", "label": "Class", "type": "text"},
                    {"field": "subject", "label": "Subject", "type": "text"},
                    {"field": "score", "label": "Score", "type": "number"},
                    {"field": "max_score", "label": "Max Score", "type": "number"},
                    {"field": "percentage", "label": "Percentage", "type": "number"},
                    {"field": "date", "label": "Date", "type": "date"},
                    {"field": "comments", "label": "Comments", "type": "text"}
                ],
                "default_columns": ["student_name", "subject", "score", "percentage"],
                "supported_formats": ["csv", "xlsx", "pdf", "json"],
                "max_records": 50000,
                "batch_size": 2000
            },
            "attendance": {
                "model": Attendance,
                "available_columns": [
                    {"field": "id", "label": "ID", "type": "number"},
                    {"field": "student_name", "label": "Student Name", "type": "text"},
                    {"field": "class_name", "label": "Class", "type": "text"},
                    {"field": "date", "label": "Date", "type": "date"},
                    {"field": "status", "label": "Status", "type": "text"},
                    {"field": "time_in", "label": "Time In", "type": "time"},
                    {"field": "time_out", "label": "Time Out", "type": "time"},
                    {"field": "notes", "label": "Notes", "type": "text"}
                ],
                "default_columns": ["student_name", "date", "status"],
                "supported_formats": ["csv", "xlsx", "pdf", "json"],
                "max_records": 100000,
                "batch_size": 5000
            }
        }
    
    async def create_export_job(self, export_request: ExportRequest, created_by: int) -> ExportJob:
        """Create a new export job"""
        # Validate entity type
        if export_request.entity_type not in self.entity_configs:
            raise ValueError(f"Unsupported entity type: {export_request.entity_type}")
        
        # Validate export format
        config = self.entity_configs[export_request.entity_type]
        if export_request.export_format.value not in config["supported_formats"]:
            raise ValueError(f"Unsupported export format: {export_request.export_format}")
        
        # Create export job
        export_job = ExportJob(
            name=export_request.name,
            description=export_request.description,
            entity_type=export_request.entity_type,
            export_format=export_request.export_format.value,
            filters=export_request.filters,
            columns=export_request.columns or config["default_columns"],
            template_id=export_request.template_id,
            created_by=created_by
        )
        
        self.db.add(export_job)
        self.db.commit()
        self.db.refresh(export_job)
        
        return export_job
    
    async def process_export_job(self, job_id: int) -> ExportJob:
        """Process an export job"""
        job = self.db.query(ExportJob).filter(ExportJob.id == job_id).first()
        if not job:
            raise ValueError(f"Export job not found: {job_id}")
        
        # Update status to processing
        job.status = ExportStatus.PROCESSING
        job.started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            start_time = time.time()
            
            # Get data based on entity type
            data = await self._get_export_data(job.entity_type, job.filters, job.columns)
            
            # Generate export file
            file_path, file_size = await self._generate_export_file(
                data, job.export_format, job.name, job.entity_type
            )
            
            # Update job with results
            job.status = ExportStatus.COMPLETED
            job.file_path = str(file_path)
            job.file_size = file_size
            job.record_count = len(data)
            job.processing_time = time.time() - start_time
            job.completed_at = datetime.utcnow()
            
        except Exception as e:
            job.status = ExportStatus.FAILED
            job.error_message = str(e)
            job.processing_time = time.time() - start_time
            job.completed_at = datetime.utcnow()
        
        self.db.commit()
        return job
    
    async def _get_export_data(self, entity_type: str, filters: Optional[Dict], columns: List[str]) -> List[Dict]:
        """Get data for export based on entity type and filters"""
        config = self.entity_configs.get(entity_type)
        if not config:
            raise ValueError(f"Unsupported entity type: {entity_type}")
        
        # Build query
        query = self.db.query(config["model"])
        
        # Apply filters
        if filters:
            query = self._apply_export_filters(query, filters, entity_type)
        
        # Get data
        entities = query.limit(config["max_records"]).all()
        
        # Format data
        return [self._format_entity_data(entity, columns, entity_type) for entity in entities]
    
    def _apply_export_filters(self, query, filters: Dict[str, Any], entity_type: str):
        """Apply filters to export query"""
        config = self.entity_configs.get(entity_type)
        if not config:
            return query
        
        filter_conditions = []
        
        for filter_key, filter_value in filters.items():
            if filter_value is None or filter_value == "":
                continue
            
            if hasattr(config["model"], filter_key):
                field = getattr(config["model"], filter_key)
                
                if isinstance(filter_value, list):
                    filter_conditions.append(field.in_(filter_value))
                elif isinstance(filter_value, dict):
                    # Handle range filters
                    if "min" in filter_value:
                        filter_conditions.append(field >= filter_value["min"])
                    if "max" in filter_value:
                        filter_conditions.append(field <= filter_value["max"])
                else:
                    filter_conditions.append(field == filter_value)
        
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))
        
        return query
    
    def _format_entity_data(self, entity: Any, columns: List[str], entity_type: str) -> Dict[str, Any]:
        """Format entity data for export"""
        data = {}
        
        for column in columns:
            if entity_type == "student":
                data.update(self._format_student_data(entity, column))
            elif entity_type == "teacher":
                data.update(self._format_teacher_data(entity, column))
            elif entity_type == "class":
                data.update(self._format_class_data(entity, column))
            elif entity_type == "grade":
                data.update(self._format_grade_data(entity, column))
            elif entity_type == "attendance":
                data.update(self._format_attendance_data(entity, column))
        
        return data
    
    def _format_student_data(self, student: Student, column: str) -> Dict[str, Any]:
        """Format student data for export"""
        if column == "id":
            return {"ID": student.id}
        elif column == "student_id":
            return {"Student ID": student.student_id}
        elif column == "admission_number":
            return {"Admission Number": student.admission_number}
        elif column == "full_name":
            return {"Full Name": student.full_name}
        elif column == "date_of_birth":
            return {"Date of Birth": student.date_of_birth.isoformat() if student.date_of_birth else None}
        elif column == "gender":
            return {"Gender": student.gender}
        elif column == "address":
            return {"Address": student.address}
        elif column == "phone":
            return {"Phone": student.phone}
        elif column == "parent_name":
            return {"Parent Name": student.parent_name}
        elif column == "parent_phone":
            return {"Parent Phone": student.parent_phone}
        elif column == "admission_date":
            return {"Admission Date": student.admission_date.isoformat() if student.admission_date else None}
        elif column == "class_name":
            return {"Class": student.class_info.name if student.class_info else "Unassigned"}
        elif column == "student_level":
            return {"Level": student.student_level}
        elif column == "status":
            return {"Status": student.status}
        return {}
    
    def _format_teacher_data(self, teacher: Teacher, column: str) -> Dict[str, Any]:
        """Format teacher data for export"""
        if column == "id":
            return {"ID": teacher.id}
        elif column == "employee_id":
            return {"Employee ID": teacher.employee_id}
        elif column == "full_name":
            return {"Full Name": teacher.full_name}
        elif column == "department":
            return {"Department": teacher.department}
        elif column == "qualification":
            return {"Qualification": teacher.qualification}
        elif column == "hire_date":
            return {"Hire Date": teacher.hire_date.isoformat() if teacher.hire_date else None}
        elif column == "phone":
            return {"Phone": teacher.phone}
        elif column == "address":
            return {"Address": teacher.address}
        elif column == "status":
            return {"Status": teacher.status}
        return {}
    
    def _format_class_data(self, class_info: Class, column: str) -> Dict[str, Any]:
        """Format class data for export"""
        if column == "id":
            return {"ID": class_info.id}
        elif column == "name":
            return {"Class Name": class_info.name}
        elif column == "grade_level":
            return {"Grade Level": class_info.grade_level}
        elif column == "capacity":
            return {"Capacity": class_info.capacity}
        elif column == "current_enrollment":
            return {"Current Enrollment": len(class_info.students)}
        elif column == "teacher_name":
            return {"Teacher": class_info.teacher.full_name if class_info.teacher else "Unassigned"}
        elif column == "academic_year":
            return {"Academic Year": class_info.academic_year}
        elif column == "is_active":
            return {"Active": class_info.is_active}
        return {}
    
    def _format_grade_data(self, grade: Grade, column: str) -> Dict[str, Any]:
        """Format grade data for export"""
        if column == "id":
            return {"ID": grade.id}
        elif column == "student_name":
            return {"Student Name": grade.student.full_name}
        elif column == "class_name":
            return {"Class": grade.student.class_info.name if grade.student.class_info else "Unassigned"}
        elif column == "subject":
            return {"Subject": grade.subject}
        elif column == "score":
            return {"Score": grade.score}
        elif column == "max_score":
            return {"Max Score": grade.max_score}
        elif column == "percentage":
            return {"Percentage": round((grade.score / grade.max_score) * 100, 2)}
        elif column == "date":
            return {"Date": grade.date.isoformat() if grade.date else None}
        elif column == "comments":
            return {"Comments": grade.comments}
        return {}
    
    def _format_attendance_data(self, attendance: Attendance, column: str) -> Dict[str, Any]:
        """Format attendance data for export"""
        if column == "id":
            return {"ID": attendance.id}
        elif column == "student_name":
            return {"Student Name": attendance.user.full_name}
        elif column == "class_name":
            student_profile = attendance.user.student_profile
            return {"Class": student_profile.class_info.name if student_profile and student_profile.class_info else "Unassigned"}
        elif column == "date":
            return {"Date": attendance.date.isoformat() if attendance.date else None}
        elif column == "status":
            return {"Status": attendance.status}
        elif column == "time_in":
            return {"Time In": attendance.time_in.isoformat() if attendance.time_in else None}
        elif column == "time_out":
            return {"Time Out": attendance.time_out.isoformat() if attendance.time_out else None}
        elif column == "notes":
            return {"Notes": attendance.notes}
        return {}
    
    async def _generate_export_file(self, data: List[Dict], export_format: str, name: str, entity_type: str) -> tuple[Path, int]:
        """Generate export file in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{entity_type}_{name}_{timestamp}"
        
        if export_format == ExportFormat.CSV:
            return await self._generate_csv(data, filename)
        elif export_format == ExportFormat.EXCEL:
            return await self._generate_excel(data, filename)
        elif export_format == ExportFormat.PDF:
            return await self._generate_pdf(data, filename, entity_type)
        elif export_format == ExportFormat.JSON:
            return await self._generate_json(data, filename)
        elif export_format == ExportFormat.XML:
            return await self._generate_xml(data, filename)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    async def _generate_csv(self, data: List[Dict], filename: str) -> tuple[Path, int]:
        """Generate CSV export file"""
        file_path = self.export_dir / f"{filename}.csv"
        
        if data:
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
        else:
            # Create empty CSV with headers
            pd.DataFrame(columns=data[0].keys() if data else []).to_csv(file_path, index=False)
        
        file_size = file_path.stat().st_size
        return file_path, file_size
    
    async def _generate_excel(self, data: List[Dict], filename: str) -> tuple[Path, int]:
        """Generate Excel export file"""
        file_path = self.export_dir / f"{filename}.xlsx"
        
        if data:
            df = pd.DataFrame(data)
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
        else:
            # Create empty Excel with headers
            df = pd.DataFrame(columns=data[0].keys() if data else [])
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
        
        file_size = file_path.stat().st_size
        return file_path, file_size
    
    async def _generate_pdf(self, data: List[Dict], filename: str, entity_type: str) -> tuple[Path, int]:
        """Generate PDF export file"""
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        file_path = self.export_dir / f"{filename}.pdf"
        
        doc = SimpleDocTemplate(str(file_path), pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Add title
        title = Paragraph(f"{entity_type.title()} Export Report", styles['Heading1'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Add generation info
        info = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
        story.append(info)
        story.append(Spacer(1, 20))
        
        if data:
            # Create table
            headers = list(data[0].keys())
            table_data = [headers]
            
            for row in data:
                table_data.append([str(row.get(header, "")) for header in headers])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
        else:
            no_data = Paragraph("No data available for export", styles['Normal'])
            story.append(no_data)
        
        doc.build(story)
        file_size = file_path.stat().st_size
        return file_path, file_size
    
    async def _generate_json(self, data: List[Dict], filename: str) -> tuple[Path, int]:
        """Generate JSON export file"""
        file_path = self.export_dir / f"{filename}.json"
        
        export_data = {
            "export_info": {
                "generated_at": datetime.now().isoformat(),
                "record_count": len(data)
            },
            "data": data
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        file_size = file_path.stat().st_size
        return file_path, file_size
    
    async def _generate_xml(self, data: List[Dict], filename: str) -> tuple[Path, int]:
        """Generate XML export file"""
        file_path = self.export_dir / f"{filename}.xml"
        
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += f'<export generated_at="{datetime.now().isoformat()}">\n'
        xml_content += f'  <record_count>{len(data)}</record_count>\n'
        xml_content += '  <data>\n'
        
        for record in data:
            xml_content += '    <record>\n'
            for key, value in record.items():
                xml_content += f'      <{key}>{value}</{key}>\n'
            xml_content += '    </record>\n'
        
        xml_content += '  </data>\n'
        xml_content += '</export>'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        file_size = file_path.stat().st_size
        return file_path, file_size
    
    async def get_export_jobs(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[ExportJob]:
        """Get export jobs with optional filtering"""
        query = self.db.query(ExportJob)
        
        if status:
            query = query.filter(ExportJob.status == status)
        
        return query.order_by(ExportJob.created_at.desc()).offset(skip).limit(limit).all()
    
    async def get_export_job_by_id(self, job_id: int) -> Optional[ExportJob]:
        """Get export job by ID"""
        return self.db.query(ExportJob).filter(ExportJob.id == job_id).first()
    
    async def cancel_export_job(self, job_id: int) -> bool:
        """Cancel an export job"""
        job = await self.get_export_job_by_id(job_id)
        if not job:
            return False
        
        if job.status in [ExportStatus.PENDING, ExportStatus.PROCESSING]:
            job.status = ExportStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    async def delete_export_job(self, job_id: int) -> bool:
        """Delete an export job and its file"""
        job = await self.get_export_job_by_id(job_id)
        if not job:
            return False
        
        # Delete file if it exists
        if job.file_path and os.path.exists(job.file_path):
            try:
                os.remove(job.file_path)
            except Exception:
                pass  # Ignore file deletion errors
        
        self.db.delete(job)
        self.db.commit()
        return True
    
    async def create_export_template(self, template_data: Dict[str, Any], created_by: int) -> ExportTemplate:
        """Create a new export template"""
        template = ExportTemplate(
            name=template_data["name"],
            description=template_data.get("description"),
            entity_type=template_data["entity_type"],
            export_format=template_data["export_format"],
            columns=template_data["columns"],
            filters=template_data.get("filters"),
            sorting=template_data.get("sorting"),
            is_default=template_data.get("is_default", False),
            created_by=created_by
        )
        
        # If this is set as default, unset other defaults for this entity type
        if template.is_default:
            self.db.query(ExportTemplate).filter(
                ExportTemplate.entity_type == template.entity_type,
                ExportTemplate.is_default == True
            ).update({"is_default": False})
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    async def get_export_templates(self, entity_type: Optional[str] = None) -> List[ExportTemplate]:
        """Get export templates"""
        query = self.db.query(ExportTemplate).filter(ExportTemplate.is_active == True)
        
        if entity_type:
            query = query.filter(ExportTemplate.entity_type == entity_type)
        
        return query.order_by(ExportTemplate.is_default.desc(), ExportTemplate.name).all()
    
    async def get_export_statistics(self) -> ExportStatistics:
        """Get export statistics"""
        now = datetime.utcnow()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Basic counts
        total_exports = self.db.query(ExportJob).count()
        exports_today = self.db.query(ExportJob).filter(
            func.date(ExportJob.created_at) == today
        ).count()
        exports_this_week = self.db.query(ExportJob).filter(
            ExportJob.created_at >= week_ago
        ).count()
        exports_this_month = self.db.query(ExportJob).filter(
            ExportJob.created_at >= month_ago
        ).count()
        
        # Average processing time
        avg_processing_time = self.db.query(func.avg(ExportJob.processing_time)).scalar() or 0
        
        # Format distribution
        format_stats = self.db.query(
            ExportJob.export_format,
            func.count(ExportJob.id).label("count")
        ).group_by(ExportJob.export_format).all()
        
        # Entity type distribution
        entity_stats = self.db.query(
            ExportJob.entity_type,
            func.count(ExportJob.id).label("count")
        ).group_by(ExportJob.entity_type).all()
        
        # User activity
        user_stats = self.db.query(
            ExportJob.created_by,
            func.count(ExportJob.id).label("count")
        ).group_by(ExportJob.created_by).order_by(
            func.count(ExportJob.id).desc()
        ).limit(10).all()
        
        return ExportStatistics(
            total_exports=total_exports,
            exports_today=exports_today,
            exports_this_week=exports_this_week,
            exports_this_month=exports_this_month,
            average_processing_time=float(avg_processing_time),
            format_distribution={stat.export_format: stat.count for stat in format_stats},
            entity_type_distribution={stat.entity_type: stat.count for stat in entity_stats},
            user_export_activity={str(stat.created_by): stat.count for stat in user_stats}
        )
    
    async def get_export_config(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """Get export configuration for entity type"""
        config = self.entity_configs.get(entity_type)
        if not config:
            return None
        
        return {
            "entity_type": entity_type,
            "available_columns": config["available_columns"],
            "default_columns": config["default_columns"],
            "supported_formats": config["supported_formats"],
            "max_records": config["max_records"],
            "batch_size": config["batch_size"]
        } 