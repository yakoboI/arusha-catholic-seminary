#!/usr/bin/env python3
"""
Test script for Phase 4 File Management System

This script tests the file upload, download, and management functionality.
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_file_management():
    """Test file management functionality"""
    
    print("🧪 Testing Phase 4: File Management System")
    print("=" * 50)
    
    # Test authentication
    print("\n1. Testing Authentication...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Test file categories
    print("\n2. Testing File Categories...")
    try:
        response = requests.get(f"{API_BASE}/files/categories/list", headers=headers)
        if response.status_code == 200:
            categories = response.json()["categories"]
            print(f"✅ Found {len(categories)} file categories:")
            for cat in categories:
                print(f"   - {cat['label']} ({cat['value']})")
        else:
            print("❌ Failed to get file categories")
    except Exception as e:
        print(f"❌ File categories error: {e}")
    
    # Test file upload
    print("\n3. Testing File Upload...")
    try:
        # Create a test file
        test_file_path = Path("test_document.txt")
        with open(test_file_path, "w") as f:
            f.write("This is a test document for file management system.")
        
        files = {"file": open(test_file_path, "rb")}
        data = {
            "category": "document",
            "description": "Test document for file management",
            "tags": "test,document,phase4",
            "is_public": "false"
        }
        
        response = requests.post(
            f"{API_BASE}/files/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            file_id = result["file_record"]["id"]
            print(f"✅ File uploaded successfully (ID: {file_id})")
            print(f"   - Filename: {result['file_record']['original_filename']}")
            print(f"   - Size: {result['file_record']['file_size']} bytes")
            print(f"   - Category: {result['file_record']['category']}")
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Clean up test file
        test_file_path.unlink()
        
    except Exception as e:
        print(f"❌ File upload error: {e}")
    
    # Test file listing
    print("\n4. Testing File Listing...")
    try:
        response = requests.get(f"{API_BASE}/files/", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['total']} files")
            print(f"   - Page: {result['page']}/{result['total_pages']}")
            print(f"   - Files per page: {result['per_page']}")
            
            if result['files']:
                print("   - Recent files:")
                for file in result['files'][:3]:
                    print(f"     * {file['original_filename']} ({file['file_size']} bytes)")
        else:
            print("❌ Failed to list files")
    except Exception as e:
        print(f"❌ File listing error: {e}")
    
    # Test storage statistics
    print("\n5. Testing Storage Statistics...")
    try:
        response = requests.get(f"{API_BASE}/files/stats/storage", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Storage Statistics:")
            print(f"   - Total files: {stats['total_files']}")
            print(f"   - Total size: {stats['total_size']} bytes")
            print(f"   - Categories: {len(stats['category_stats'])}")
        else:
            print("❌ Failed to get storage statistics")
    except Exception as e:
        print(f"❌ Storage statistics error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 File Management System Test Complete!")

if __name__ == "__main__":
    test_file_management() 