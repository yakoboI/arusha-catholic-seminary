#!/usr/bin/env python3
"""
Test the clean server
"""

import requests
import time

def test_server():
    """Test if the clean server is working"""
    print("🔍 Testing Clean Arusha Catholic Seminary Server...")
    
    # Wait a moment for server to start
    time.sleep(3)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and healthy!")
            print(f"   Response: {response.json()}")
            
            # Test root endpoint
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ Root endpoint working!")
                print(f"   Message: {response.json().get('message')}")
            
            # Test login endpoint
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data, timeout=5)
            if response.status_code == 200:
                print("✅ Login endpoint working!")
                print(f"   Login successful: {response.json().get('message')}")
            else:
                print(f"❌ Login failed: {response.status_code}")
            
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server on localhost:8000")
        print("   Make sure the server is running with: python server.py")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    test_server()
