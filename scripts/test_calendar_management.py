#!/usr/bin/env python3
"""
Calendar Management System Test Script

This script tests the calendar management functionality including:
- Event categories CRUD operations
- Calendar events CRUD operations
- Event participants management
- iCal export functionality
- Calendar statistics and search
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, 'backend')

import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Initialize Rich console
console = Console()

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test data
TEST_CATEGORY = {
    "name": "Academic Events",
    "description": "Academic-related events and activities",
    "color": "#3B82F6",
    "icon": "graduation-cap"
}

TEST_EVENT = {
    "title": "Parent-Teacher Conference",
    "description": "Annual parent-teacher conference for all classes",
    "event_type": "meeting",
    "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
    "end_date": (datetime.now() + timedelta(days=7, hours=2)).isoformat(),
    "all_day": False,
    "start_time": "14:00:00",
    "end_time": "16:00:00",
    "location": "Main Hall",
    "room": "Auditorium",
    "priority": "high",
    "tags": ["academic", "parents", "teachers"]
}

TEST_PARTICIPANT = {
    "user_id": 1,
    "role": "attendee",
    "status": "invited",
    "notes": "Parent representative"
}

class CalendarManagementTester:
    """Test calendar management functionality"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.category_id = None
        self.event_id = None
        self.participant_id = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        console.print(f"{status} {test_name}")
        if details:
            console.print(f"   {details}")
    
    async def test_health_check(self) -> bool:
        """Test if the server is running"""
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log_test("Health Check", True, "Server is running")
                return True
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    async def test_create_category(self) -> bool:
        """Test creating an event category"""
        try:
            response = await self.client.post(
                f"{API_BASE}/calendar/categories",
                json=TEST_CATEGORY
            )
            
            if response.status_code == 201:
                data = response.json()
                self.category_id = data["id"]
                self.log_test("Create Category", True, f"Category ID: {self.category_id}")
                return True
            else:
                self.log_test("Create Category", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Category", False, f"Error: {str(e)}")
            return False
    
    async def test_get_categories(self) -> bool:
        """Test retrieving event categories"""
        try:
            response = await self.client.get(f"{API_BASE}/calendar/categories")
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get("items", [])
                self.log_test("Get Categories", True, f"Found {len(categories)} categories")
                return True
            else:
                self.log_test("Get Categories", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Categories", False, f"Error: {str(e)}")
            return False
    
    async def test_create_event(self) -> bool:
        """Test creating a calendar event"""
        if not self.category_id:
            self.log_test("Create Event", False, "No category ID available")
            return False
            
        event_data = TEST_EVENT.copy()
        event_data["category_id"] = self.category_id
        
        try:
            response = await self.client.post(
                f"{API_BASE}/calendar/events",
                json=event_data
            )
            
            if response.status_code == 201:
                data = response.json()
                self.event_id = data["id"]
                self.log_test("Create Event", True, f"Event ID: {self.event_id}")
                return True
            else:
                self.log_test("Create Event", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Event", False, f"Error: {str(e)}")
            return False
    
    async def test_get_events(self) -> bool:
        """Test retrieving calendar events"""
        try:
            response = await self.client.get(f"{API_BASE}/calendar/events")
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("items", [])
                self.log_test("Get Events", True, f"Found {len(events)} events")
                return True
            else:
                self.log_test("Get Events", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Events", False, f"Error: {str(e)}")
            return False
    
    async def test_get_event_by_id(self) -> bool:
        """Test retrieving a specific event"""
        if not self.event_id:
            self.log_test("Get Event by ID", False, "No event ID available")
            return False
            
        try:
            response = await self.client.get(f"{API_BASE}/calendar/events/{self.event_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Event by ID", True, f"Event: {data['title']}")
                return True
            else:
                self.log_test("Get Event by ID", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Event by ID", False, f"Error: {str(e)}")
            return False
    
    async def test_update_event(self) -> bool:
        """Test updating an event"""
        if not self.event_id:
            self.log_test("Update Event", False, "No event ID available")
            return False
            
        update_data = {
            "title": "Updated Parent-Teacher Conference",
            "description": "Updated description for the conference",
            "priority": "urgent"
        }
        
        try:
            response = await self.client.put(
                f"{API_BASE}/calendar/events/{self.event_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Update Event", True, f"Updated: {data['title']}")
                return True
            else:
                self.log_test("Update Event", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Update Event", False, f"Error: {str(e)}")
            return False
    
    async def test_add_participant(self) -> bool:
        """Test adding a participant to an event"""
        if not self.event_id:
            self.log_test("Add Participant", False, "No event ID available")
            return False
            
        try:
            response = await self.client.post(
                f"{API_BASE}/calendar/events/{self.event_id}/participants",
                json=TEST_PARTICIPANT
            )
            
            if response.status_code == 201:
                data = response.json()
                self.participant_id = data["id"]
                self.log_test("Add Participant", True, f"Participant ID: {self.participant_id}")
                return True
            else:
                self.log_test("Add Participant", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Add Participant", False, f"Error: {str(e)}")
            return False
    
    async def test_get_participants(self) -> bool:
        """Test retrieving event participants"""
        if not self.event_id:
            self.log_test("Get Participants", False, "No event ID available")
            return False
            
        try:
            response = await self.client.get(f"{API_BASE}/calendar/events/{self.event_id}/participants")
            
            if response.status_code == 200:
                data = response.json()
                participants = data.get("items", [])
                self.log_test("Get Participants", True, f"Found {len(participants)} participants")
                return True
            else:
                self.log_test("Get Participants", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Participants", False, f"Error: {str(e)}")
            return False
    
    async def test_update_participant(self) -> bool:
        """Test updating a participant"""
        if not self.participant_id:
            self.log_test("Update Participant", False, "No participant ID available")
            return False
            
        update_data = {
            "status": "accepted",
            "notes": "Confirmed attendance"
        }
        
        try:
            response = await self.client.put(
                f"{API_BASE}/calendar/participants/{self.participant_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Update Participant", True, f"Status: {data['status']}")
                return True
            else:
                self.log_test("Update Participant", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Update Participant", False, f"Error: {str(e)}")
            return False
    
    async def test_calendar_search(self) -> bool:
        """Test calendar search functionality"""
        try:
            params = {
                "q": "conference",
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            response = await self.client.get(f"{API_BASE}/calendar/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("items", [])
                self.log_test("Calendar Search", True, f"Found {len(events)} matching events")
                return True
            else:
                self.log_test("Calendar Search", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Calendar Search", False, f"Error: {str(e)}")
            return False
    
    async def test_calendar_stats(self) -> bool:
        """Test calendar statistics"""
        try:
            response = await self.client.get(f"{API_BASE}/calendar/stats")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Calendar Stats", True, f"Total events: {data.get('total_events', 0)}")
                return True
            else:
                self.log_test("Calendar Stats", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Calendar Stats", False, f"Error: {str(e)}")
            return False
    
    async def test_ical_export(self) -> bool:
        """Test iCal export functionality"""
        try:
            response = await self.client.get(f"{API_BASE}/calendar/export/ical")
            
            if response.status_code == 200:
                content = response.text
                if "BEGIN:VCALENDAR" in content and "END:VCALENDAR" in content:
                    self.log_test("iCal Export", True, f"Generated {len(content)} characters")
                    return True
                else:
                    self.log_test("iCal Export", False, "Invalid iCal format")
                    return False
            else:
                self.log_test("iCal Export", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("iCal Export", False, f"Error: {str(e)}")
            return False
    
    async def test_delete_participant(self) -> bool:
        """Test deleting a participant"""
        if not self.participant_id:
            self.log_test("Delete Participant", False, "No participant ID available")
            return False
            
        try:
            response = await self.client.delete(f"{API_BASE}/calendar/participants/{self.participant_id}")
            
            if response.status_code == 204:
                self.log_test("Delete Participant", True, "Participant deleted successfully")
                return True
            else:
                self.log_test("Delete Participant", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Delete Participant", False, f"Error: {str(e)}")
            return False
    
    async def test_delete_event(self) -> bool:
        """Test deleting an event"""
        if not self.event_id:
            self.log_test("Delete Event", False, "No event ID available")
            return False
            
        try:
            response = await self.client.delete(f"{API_BASE}/calendar/events/{self.event_id}")
            
            if response.status_code == 204:
                self.log_test("Delete Event", True, "Event deleted successfully")
                return True
            else:
                self.log_test("Delete Event", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Delete Event", False, f"Error: {str(e)}")
            return False
    
    async def test_delete_category(self) -> bool:
        """Test deleting a category"""
        if not self.category_id:
            self.log_test("Delete Category", False, "No category ID available")
            return False
            
        try:
            response = await self.client.delete(f"{API_BASE}/calendar/categories/{self.category_id}")
            
            if response.status_code == 204:
                self.log_test("Delete Category", True, "Category deleted successfully")
                return True
            else:
                self.log_test("Delete Category", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Delete Category", False, f"Error: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        console.print("\n" + "="*60)
        console.print("[bold blue]CALENDAR MANAGEMENT SYSTEM TEST SUMMARY[/bold blue]")
        console.print("="*60)
        
        # Create summary table
        table = Table(title="Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            table.add_row(result["test"], status, result["details"])
        
        console.print(table)
        
        # Print statistics
        console.print(f"\n[bold]Statistics:[/bold]")
        console.print(f"Total Tests: {total_tests}")
        console.print(f"Passed: {passed_tests} ✅")
        console.print(f"Failed: {failed_tests} ❌")
        console.print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            console.print("\n[bold green]🎉 ALL TESTS PASSED! Calendar Management System is working correctly.[/bold green]")
        else:
            console.print(f"\n[bold red]⚠️  {failed_tests} test(s) failed. Please check the implementation.[/bold red]")
        
        return failed_tests == 0

async def main():
    """Main test function"""
    console.print(Panel.fit(
        "[bold blue]Calendar Management System Test Suite[/bold blue]\n"
        "Testing calendar integration functionality...",
        border_style="blue"
    ))
    
    async with CalendarManagementTester() as tester:
        # Test sequence
        tests = [
            ("Health Check", tester.test_health_check),
            ("Create Category", tester.test_create_category),
            ("Get Categories", tester.test_get_categories),
            ("Create Event", tester.test_create_event),
            ("Get Events", tester.test_get_events),
            ("Get Event by ID", tester.test_get_event_by_id),
            ("Update Event", tester.test_update_event),
            ("Add Participant", tester.test_add_participant),
            ("Get Participants", tester.test_get_participants),
            ("Update Participant", tester.test_update_participant),
            ("Calendar Search", tester.test_calendar_search),
            ("Calendar Stats", tester.test_calendar_stats),
            ("iCal Export", tester.test_ical_export),
            ("Delete Participant", tester.test_delete_participant),
            ("Delete Event", tester.test_delete_event),
            ("Delete Category", tester.test_delete_category),
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running tests...", total=len(tests))
            
            for test_name, test_func in tests:
                progress.update(task, description=f"Running {test_name}...")
                await test_func()
                progress.advance(task)
                await asyncio.sleep(0.1)  # Small delay for better UX
        
        # Print summary
        success = tester.print_summary()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"logs/calendar_management_test_{timestamp}.json"
        
        try:
            import os
            os.makedirs("logs", exist_ok=True)
            
            with open(results_file, "w") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_tests": len(tester.test_results),
                    "passed_tests": sum(1 for r in tester.test_results if r["success"]),
                    "failed_tests": sum(1 for r in tester.test_results if not r["success"]),
                    "results": tester.test_results
                }, f, indent=2)
            
            console.print(f"\n[dim]Test results saved to: {results_file}[/dim]")
        except Exception as e:
            console.print(f"\n[dim]Could not save results: {e}[/dim]")
        
        return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1) 