#!/usr/bin/env python3
"""
Report Management System Test Script

This script tests the report management functionality including:
- Template creation and management
- Report generation (PDF, Excel, CSV, HTML, JSON)
- Report downloading and statistics
- Quick report generation endpoints
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_report_management():
    """Test report management functionality"""
    print("📊 Testing Report Management System")
    print("=" * 50)
    
    # 1. Authentication
    print("\n1. Authenticating...")
    try:
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            print(f"✅ Authentication successful")
            print(f"   - User: {token_data['user']['full_name']}")
            print(f"   - Role: {token_data['user']['role']}")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # 2. Get report types and formats
    print("\n2. Getting Report Types and Formats...")
    try:
        # Get report types
        response = requests.get(f"{API_BASE}/reports/types", headers=headers)
        if response.status_code == 200:
            report_types = response.json()
            print(f"✅ Report types retrieved: {len(report_types['report_types'])} types")
            for report_type in report_types['report_types']:
                print(f"   - {report_type['label']} ({report_type['value']})")
        else:
            print(f"❌ Failed to get report types: {response.status_code}")
        
        # Get report formats
        response = requests.get(f"{API_BASE}/reports/formats", headers=headers)
        if response.status_code == 200:
            report_formats = response.json()
            print(f"✅ Report formats retrieved: {len(report_formats['report_formats'])} formats")
            for format_type in report_formats['report_formats']:
                print(f"   - {format_type['label']} ({format_type['value']})")
        else:
            print(f"❌ Failed to get report formats: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting report types/formats: {e}")
    
    # 3. Create report template
    print("\n3. Creating Report Template...")
    try:
        template_data = {
            "name": "student_list_template",
            "description": "Template for generating student list reports",
            "report_type": "student_list",
            "template_config": {
                "title": "Student List Report",
                "include_header": True,
                "include_footer": True,
                "page_size": "A4",
                "orientation": "portrait"
            },
            "query_config": {
                "base_query": "SELECT * FROM students",
                "filters": ["class_id", "student_level"],
                "sorting": ["full_name"]
            },
            "output_formats": ["pdf", "excel", "csv"],
            "parameters": {
                "class_id": {"type": "integer", "required": False},
                "student_level": {"type": "string", "required": False}
            },
            "is_active": True
        }
        
        response = requests.post(
            f"{API_BASE}/reports/templates",
            json=template_data,
            headers=headers
        )
        
        if response.status_code == 201:
            template = response.json()
            template_id = template["id"]
            print(f"✅ Report template created successfully (ID: {template_id})")
            print(f"   - Name: {template['name']}")
            print(f"   - Type: {template['report_type']}")
            print(f"   - Formats: {template['output_formats']}")
        else:
            print(f"❌ Template creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Template creation error: {e}")
        return
    
    # 4. Generate student list report (PDF)
    print("\n4. Generating Student List Report (PDF)...")
    try:
        report_data = {
            "template_name": "student_list_template",
            "report_type": "student_list",
            "output_format": "pdf",
            "parameters": {
                "student_level": "O-Level"
            }
        }
        
        response = requests.post(
            f"{API_BASE}/reports/generate",
            json=report_data,
            headers=headers
        )
        
        if response.status_code == 202:
            result = response.json()
            print(f"✅ Student list report generation started")
            print(f"   - Message: {result['message']}")
        else:
            print(f"❌ Report generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Report generation error: {e}")
    
    # 5. Generate grade report (Excel)
    print("\n5. Generating Grade Report (Excel)...")
    try:
        report_data = {
            "report_type": "grade_report",
            "output_format": "excel",
            "parameters": {
                "academic_year": "2024",
                "semester": "First Term"
            }
        }
        
        response = requests.post(
            f"{API_BASE}/reports/generate",
            json=report_data,
            headers=headers
        )
        
        if response.status_code == 202:
            result = response.json()
            print(f"✅ Grade report generation started")
            print(f"   - Message: {result['message']}")
        else:
            print(f"❌ Report generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Report generation error: {e}")
    
    # 6. Generate attendance report (CSV)
    print("\n6. Generating Attendance Report (CSV)...")
    try:
        report_data = {
            "report_type": "attendance_report",
            "output_format": "csv",
            "parameters": {
                "date_from": "2024-01-01",
                "date_to": "2024-12-31"
            }
        }
        
        response = requests.post(
            f"{API_BASE}/reports/generate",
            json=report_data,
            headers=headers
        )
        
        if response.status_code == 202:
            result = response.json()
            print(f"✅ Attendance report generation started")
            print(f"   - Message: {result['message']}")
        else:
            print(f"❌ Report generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Report generation error: {e}")
    
    # 7. Generate financial report (HTML)
    print("\n7. Generating Financial Report (HTML)...")
    try:
        report_data = {
            "report_type": "financial_report",
            "output_format": "html",
            "parameters": {
                "date_from": "2024-01-01",
                "date_to": "2024-12-31"
            }
        }
        
        response = requests.post(
            f"{API_BASE}/reports/generate",
            json=report_data,
            headers=headers
        )
        
        if response.status_code == 202:
            result = response.json()
            print(f"✅ Financial report generation started")
            print(f"   - Message: {result['message']}")
        else:
            print(f"❌ Report generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Report generation error: {e}")
    
    # 8. Wait a moment for reports to process
    print("\n8. Waiting for reports to process...")
    time.sleep(5)
    
    # 9. Get report logs
    print("\n9. Retrieving Report Logs...")
    try:
        response = requests.get(
            f"{API_BASE}/reports/logs?limit=10",
            headers=headers
        )
        
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Report logs retrieved: {len(logs)} logs")
            for log in logs[:3]:  # Show first 3 logs
                print(f"   - {log['report_name']} | {log['report_type']} | {log['status']} | {log['created_at']}")
        else:
            print(f"❌ Failed to get report logs: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting report logs: {e}")
    
    # 10. Get report statistics
    print("\n10. Retrieving Report Statistics...")
    try:
        response = requests.get(
            f"{API_BASE}/reports/stats?days=30",
            headers=headers
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Report statistics retrieved")
            print(f"   - Total Reports: {stats['total_reports']}")
            print(f"   - Total Templates: {stats['total_templates']}")
            print(f"   - Success Rate: {stats['success_rate']:.1f}%")
            print(f"   - Avg Processing Time: {stats['processing_time_avg']:.2f}s")
            
            if stats['reports_by_type']:
                print(f"   - Reports by Type:")
                for report_type, count in stats['reports_by_type'].items():
                    print(f"     * {report_type}: {count}")
        else:
            print(f"❌ Failed to get report statistics: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting report statistics: {e}")
    
    # 11. Test quick report generation endpoints
    print("\n11. Testing Quick Report Generation...")
    try:
        # Quick student list report
        response = requests.post(
            f"{API_BASE}/reports/quick/student-list?output_format=pdf",
            headers=headers
        )
        
        if response.status_code == 202:
            result = response.json()
            print(f"✅ Quick student list report started")
            print(f"   - Message: {result['message']}")
        else:
            print(f"❌ Quick student list report failed: {response.status_code}")
        
        # Quick grade report
        response = requests.post(
            f"{API_BASE}/reports/quick/grade-report?output_format=excel&academic_year=2024",
            headers=headers
        )
        
        if response.status_code == 202:
            result = response.json()
            print(f"✅ Quick grade report started")
            print(f"   - Message: {result['message']}")
        else:
            print(f"❌ Quick grade report failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Quick report generation error: {e}")
    
    # 12. List report templates
    print("\n12. Listing Report Templates...")
    try:
        response = requests.get(
            f"{API_BASE}/reports/templates",
            headers=headers
        )
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Report templates retrieved: {len(templates)} templates")
            for template in templates:
                print(f"   - {template['name']} ({template['report_type']}) - {'Active' if template['is_active'] else 'Inactive'}")
        else:
            print(f"❌ Failed to get report templates: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting report templates: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Report Management System Test Completed!")
    print("\nNote: Report generation is asynchronous. Check the logs for completion status.")
    print("Download generated reports using the /reports/logs/{log_id}/download endpoint.")

if __name__ == "__main__":
    test_report_management() 