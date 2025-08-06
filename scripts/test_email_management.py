#!/usr/bin/env python3
"""
Email Management System Test Script

This script tests the email management functionality including:
- Template creation and management
- Email sending (single and bulk)
- Email logging and statistics
- Template preview functionality
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

def test_email_management():
    """Test email management functionality"""
    print("🚀 Testing Email Management System")
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
    
    # 2. Get email types and statuses
    print("\n2. Getting Email Types and Statuses...")
    try:
        # Get email types
        response = requests.get(f"{API_BASE}/email/types", headers=headers)
        if response.status_code == 200:
            email_types = response.json()
            print(f"✅ Email types retrieved: {len(email_types['email_types'])} types")
            for email_type in email_types['email_types']:
                print(f"   - {email_type['label']} ({email_type['value']})")
        else:
            print(f"❌ Failed to get email types: {response.status_code}")
        
        # Get email statuses
        response = requests.get(f"{API_BASE}/email/statuses", headers=headers)
        if response.status_code == 200:
            email_statuses = response.json()
            print(f"✅ Email statuses retrieved: {len(email_statuses['email_statuses'])} statuses")
            for status in email_statuses['email_statuses']:
                print(f"   - {status['label']} ({status['value']})")
        else:
            print(f"❌ Failed to get email statuses: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting email types/statuses: {e}")
    
    # 3. Create email template
    print("\n3. Creating Email Template...")
    try:
        template_data = {
            "name": "welcome_student",
            "subject": "Welcome to Arusha Catholic Seminary, {{student_name}}!",
            "body_html": """
            <html>
            <body>
                <h2>Welcome to Arusha Catholic Seminary!</h2>
                <p>Dear {{student_name}},</p>
                <p>Welcome to our seminary! We are excited to have you join our community.</p>
                <p><strong>Student Details:</strong></p>
                <ul>
                    <li>Student ID: {{student_id}}</li>
                    <li>Class: {{class_name}}</li>
                    <li>Admission Date: {{admission_date}}</li>
                </ul>
                <p>Best regards,<br>Arusha Catholic Seminary</p>
            </body>
            </html>
            """,
            "body_text": """
            Welcome to Arusha Catholic Seminary!
            
            Dear {{student_name}},
            
            Welcome to our seminary! We are excited to have you join our community.
            
            Student Details:
            - Student ID: {{student_id}}
            - Class: {{class_name}}
            - Admission Date: {{admission_date}}
            
            Best regards,
            Arusha Catholic Seminary
            """,
            "email_type": "welcome",
            "variables": {
                "student_name": "string",
                "student_id": "string", 
                "class_name": "string",
                "admission_date": "date"
            },
            "is_active": True
        }
        
        response = requests.post(
            f"{API_BASE}/email/templates",
            json=template_data,
            headers=headers
        )
        
        if response.status_code == 201:
            template = response.json()
            template_id = template["id"]
            print(f"✅ Email template created successfully (ID: {template_id})")
            print(f"   - Name: {template['name']}")
            print(f"   - Type: {template['email_type']}")
            print(f"   - Subject: {template['subject']}")
        else:
            print(f"❌ Template creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Template creation error: {e}")
        return
    
    # 4. Preview email template
    print("\n4. Previewing Email Template...")
    try:
        preview_variables = {
            "student_name": "John Doe",
            "student_id": "STU001",
            "class_name": "Form 1A",
            "admission_date": "2024-01-15"
        }
        
        response = requests.post(
            f"{API_BASE}/email/templates/{template_id}/preview",
            json=preview_variables,
            headers=headers
        )
        
        if response.status_code == 200:
            preview = response.json()
            print(f"✅ Template preview generated successfully")
            print(f"   - Subject: {preview['subject']}")
            print(f"   - HTML Body Length: {len(preview['body_html'])} characters")
            if preview.get('body_text'):
                print(f"   - Text Body Length: {len(preview['body_text'])} characters")
        else:
            print(f"❌ Template preview failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Template preview error: {e}")
    
    # 5. Send test email (using template)
    print("\n5. Sending Test Email (using template)...")
    try:
        email_data = {
            "recipient_email": "test@example.com",
            "recipient_name": "Test User",
            "template_name": "welcome_student",
            "email_type": "welcome",
            "variables": {
                "student_name": "Test Student",
                "student_id": "TEST001",
                "class_name": "Form 1A",
                "admission_date": "2024-01-15"
            },
            "metadata": {
                "test": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        response = requests.post(
            f"{API_BASE}/email/send",
            json=email_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test email sent successfully")
            print(f"   - Message: {result['message']}")
        else:
            print(f"❌ Email sending failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
    
    # 6. Send test email (direct content)
    print("\n6. Sending Test Email (direct content)...")
    try:
        email_data = {
            "recipient_email": "direct@example.com",
            "recipient_name": "Direct User",
            "subject": "Direct Email Test",
            "body_html": """
            <html>
            <body>
                <h2>Direct Email Test</h2>
                <p>This is a test email sent with direct content.</p>
                <p>Timestamp: {{timestamp}}</p>
            </body>
            </html>
            """,
            "body_text": "Direct Email Test\n\nThis is a test email sent with direct content.",
            "email_type": "system_notification",
            "metadata": {
                "test": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        response = requests.post(
            f"{API_BASE}/email/send",
            json=email_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct email sent successfully")
            print(f"   - Message: {result['message']}")
        else:
            print(f"❌ Direct email sending failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Direct email sending error: {e}")
    
    # 7. Send bulk emails
    print("\n7. Sending Bulk Emails...")
    try:
        bulk_email_data = {
            "recipient_emails": [
                "bulk1@example.com",
                "bulk2@example.com",
                "bulk3@example.com"
            ],
            "template_name": "welcome_student",
            "email_type": "bulk_announcement",
            "variables": {
                "student_name": "Bulk Student",
                "student_id": "BULK001",
                "class_name": "Form 1A",
                "admission_date": "2024-01-15"
            },
            "metadata": {
                "test": True,
                "bulk_test": True
            }
        }
        
        response = requests.post(
            f"{API_BASE}/email/send/bulk",
            json=bulk_email_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Bulk email operation completed")
            print(f"   - Total: {result['results']['total']}")
            print(f"   - Sent: {result['results']['sent']}")
            print(f"   - Failed: {result['results']['failed']}")
            if result['results']['errors']:
                print(f"   - Errors: {len(result['results']['errors'])}")
        else:
            print(f"❌ Bulk email sending failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Bulk email sending error: {e}")
    
    # 8. Get email logs
    print("\n8. Retrieving Email Logs...")
    try:
        response = requests.get(
            f"{API_BASE}/email/logs?limit=10",
            headers=headers
        )
        
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Email logs retrieved: {len(logs)} logs")
            for log in logs[:3]:  # Show first 3 logs
                print(f"   - {log['recipient_email']} | {log['email_type']} | {log['status']} | {log['created_at']}")
        else:
            print(f"❌ Failed to get email logs: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting email logs: {e}")
    
    # 9. Get email statistics
    print("\n9. Retrieving Email Statistics...")
    try:
        response = requests.get(
            f"{API_BASE}/email/stats?days=30",
            headers=headers
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Email statistics retrieved")
            print(f"   - Total Sent: {stats['total_sent']}")
            print(f"   - Total Delivered: {stats['total_delivered']}")
            print(f"   - Total Failed: {stats['total_failed']}")
            print(f"   - Total Pending: {stats['total_pending']}")
            print(f"   - Delivery Rate: {stats['delivery_rate']:.1f}%")
            print(f"   - Failure Rate: {stats['failure_rate']:.1f}%")
            
            if stats['emails_by_type']:
                print(f"   - Emails by Type:")
                for email_type, count in stats['emails_by_type'].items():
                    print(f"     * {email_type}: {count}")
        else:
            print(f"❌ Failed to get email statistics: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting email statistics: {e}")
    
    # 10. List email templates
    print("\n10. Listing Email Templates...")
    try:
        response = requests.get(
            f"{API_BASE}/email/templates",
            headers=headers
        )
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Email templates retrieved: {len(templates)} templates")
            for template in templates:
                print(f"   - {template['name']} ({template['email_type']}) - {'Active' if template['is_active'] else 'Inactive'}")
        else:
            print(f"❌ Failed to get email templates: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting email templates: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Email Management System Test Completed!")
    print("\nNote: Actual email delivery depends on SMTP configuration.")
    print("Check the email logs and statistics for detailed results.")

if __name__ == "__main__":
    test_email_management() 