#!/usr/bin/env python3
"""
Test Monitoring System

This script tests the monitoring system functionality including health checks,
metrics collection, and alerting.
"""

import asyncio
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_health_endpoints():
    """Test health check endpoints"""
    print("🔍 Testing Health Endpoints...")
    
    # Test basic health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Basic health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
    except Exception as e:
        print(f"❌ Basic health check failed: {e}")
    
    # Test detailed health check
    try:
        response = requests.get(f"{BASE_URL}/health/detailed")
        print(f"✅ Detailed health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Overall Status: {data.get('status')}")
            print(f"   Response Time: {data.get('response_time_ms')}ms")
            print(f"   Unhealthy Components: {data.get('unhealthy_components')}")
    except Exception as e:
        print(f"❌ Detailed health check failed: {e}")
    
    # Test monitoring health check
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/health")
        print(f"✅ Monitoring health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Response Time: {data.get('response_time_ms')}ms")
    except Exception as e:
        print(f"❌ Monitoring health check failed: {e}")

def test_metrics_endpoints():
    """Test metrics endpoints"""
    print("\n📊 Testing Metrics Endpoints...")
    
    # Test Prometheus metrics
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/metrics")
        print(f"✅ Prometheus metrics: {response.status_code}")
        if response.status_code == 200:
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Content Length: {len(response.text)} characters")
            # Check if it contains Prometheus format
            if "# HELP" in response.text and "# TYPE" in response.text:
                print("   ✅ Valid Prometheus format")
            else:
                print("   ❌ Invalid Prometheus format")
    except Exception as e:
        print(f"❌ Prometheus metrics failed: {e}")
    
    # Test metrics summary
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/metrics/summary")
        print(f"✅ Metrics summary: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Uptime: {data.get('uptime_seconds')} seconds")
            print(f"   Total Requests: {data.get('requests', {}).get('total', 0)}")
            print(f"   Error Rate: {data.get('requests', {}).get('error_rate_percent', 0)}%")
    except Exception as e:
        print(f"❌ Metrics summary failed: {e}")

def test_dashboard_endpoints():
    """Test dashboard endpoints"""
    print("\n📈 Testing Dashboard Endpoints...")
    
    # Test dashboard data
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/dashboard")
        print(f"✅ Dashboard data: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   System Status: {data.get('system', {}).get('status')}")
            print(f"   Health Status: {data.get('health', {}).get('overall_status')}")
            print(f"   Active Alerts: {len(data.get('alerts', {}).get('active_alerts', []))}")
    except Exception as e:
        print(f"❌ Dashboard data failed: {e}")
    
    # Test dashboard HTML
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/dashboard/html")
        print(f"✅ Dashboard HTML: {response.status_code}")
        if response.status_code == 200:
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Content Length: {len(response.text)} characters")
            if "<html" in response.text and "Monitoring Dashboard" in response.text:
                print("   ✅ Valid HTML dashboard")
            else:
                print("   ❌ Invalid HTML dashboard")
    except Exception as e:
        print(f"❌ Dashboard HTML failed: {e}")

def test_alert_endpoints():
    """Test alert endpoints (requires authentication)"""
    print("\n🚨 Testing Alert Endpoints...")
    
    # First, get authentication token
    try:
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test alerts summary
            response = requests.get(f"{BASE_URL}/api/v1/monitoring/alerts/summary", headers=headers)
            print(f"✅ Alerts summary: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Total Alerts: {data.get('total_alerts', 0)}")
                print(f"   Active Alerts: {data.get('active_alerts', 0)}")
                print(f"   Resolved Alerts: {data.get('resolved_alerts', 0)}")
            
            # Test active alerts
            response = requests.get(f"{BASE_URL}/api/v1/monitoring/alerts", headers=headers)
            print(f"✅ Active alerts: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Alert Count: {data.get('total_count', 0)}")
                for alert in data.get('alerts', [])[:3]:  # Show first 3 alerts
                    print(f"   - {alert.get('title')} ({alert.get('severity')})")
        else:
            print(f"❌ Login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Alert endpoints failed: {e}")

def test_system_status():
    """Test system status endpoints"""
    print("\n🔧 Testing System Status Endpoints...")
    
    endpoints = [
        ("/api/v1/monitoring/status", "System Status"),
        ("/api/v1/monitoring/components", "Component Status"),
        ("/api/v1/monitoring/performance", "Performance Metrics"),
        ("/api/v1/monitoring/business", "Business Metrics")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✅ {name}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
        except Exception as e:
            print(f"❌ {name} failed: {e}")

def generate_test_load():
    """Generate some test load to create metrics"""
    print("\n⚡ Generating Test Load...")
    
    # Make some requests to generate metrics
    test_endpoints = [
        "/",
        "/health",
        "/info",
        "/api/v1/auth/me"  # This will fail without auth, but will generate error metrics
    ]
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")
    
    # Wait a moment for metrics to be processed
    time.sleep(2)

def main():
    """Main test function"""
    print("🚀 Arusha Catholic Seminary - Monitoring System Test")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running on http://localhost:8000")
        return
    
    print("✅ Server is running")
    
    # Run tests
    test_health_endpoints()
    test_metrics_endpoints()
    test_dashboard_endpoints()
    test_alert_endpoints()
    test_system_status()
    
    # Generate test load
    generate_test_load()
    
    # Test metrics again after load
    print("\n🔄 Testing Metrics After Load Generation...")
    test_metrics_endpoints()
    
    print("\n✅ Monitoring System Test Complete!")
    print("\n📋 Next Steps:")
    print("1. Visit http://localhost:8000/api/v1/monitoring/dashboard/html for the dashboard")
    print("2. Check http://localhost:8000/api/v1/monitoring/metrics for Prometheus metrics")
    print("3. Monitor logs for alert generation")
    print("4. Use the API endpoints for programmatic access")

if __name__ == "__main__":
    main() 