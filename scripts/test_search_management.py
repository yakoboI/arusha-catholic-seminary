#!/usr/bin/env python3
"""
Search Management System Test Script

This script tests the search management functionality including:
- Advanced search with filtering and pagination
- Search configuration retrieval
- Search suggestions and autocomplete
- Search statistics and analytics
- Search index management
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
TEST_SEARCH_REQUEST = {
    "query": "john",
    "entity_type": "student",
    "filters": {
        "status": "active"
    },
    "page": 1,
    "page_size": 10,
    "sort_by": "name",
    "sort_order": "asc"
}

TEST_GLOBAL_SEARCH = {
    "query": "teacher",
    "page": 1,
    "page_size": 20,
    "sort_order": "asc"
}

class SearchManagementTester:
    """Test search management functionality"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        
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
    
    async def test_search_students(self) -> bool:
        """Test searching for students"""
        try:
            response = await self.client.post(
                f"{API_BASE}/search/",
                json=TEST_SEARCH_REQUEST
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Search Students", True, f"Found {data['total_count']} results in {data['search_time_ms']}ms")
                return True
            else:
                self.log_test("Search Students", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Search Students", False, f"Error: {str(e)}")
            return False
    
    async def test_global_search(self) -> bool:
        """Test global search across all entities"""
        try:
            response = await self.client.post(
                f"{API_BASE}/search/",
                json=TEST_GLOBAL_SEARCH
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Global Search", True, f"Found {data['total_count']} results across all entities")
                return True
            else:
                self.log_test("Global Search", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Global Search", False, f"Error: {str(e)}")
            return False
    
    async def test_search_with_filters(self) -> bool:
        """Test search with advanced filters"""
        try:
            search_request = {
                "query": "",
                "entity_type": "student",
                "filters": {
                    "class_id": 1,
                    "status": "active"
                },
                "page": 1,
                "page_size": 5
            }
            
            response = await self.client.post(
                f"{API_BASE}/search/",
                json=search_request
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Search with Filters", True, f"Applied filters, found {data['total_count']} results")
                return True
            else:
                self.log_test("Search with Filters", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Search with Filters", False, f"Error: {str(e)}")
            return False
    
    async def test_get_search_config(self) -> bool:
        """Test getting search configuration"""
        try:
            response = await self.client.get(f"{API_BASE}/search/config/student")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Search Config", True, f"Config for student entity with {len(data.get('filters', []))} filters")
                return True
            else:
                self.log_test("Get Search Config", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Search Config", False, f"Error: {str(e)}")
            return False
    
    async def test_get_all_search_configs(self) -> bool:
        """Test getting all search configurations"""
        try:
            response = await self.client.get(f"{API_BASE}/search/config")
            
            if response.status_code == 200:
                data = response.json()
                entity_count = len(data)
                self.log_test("Get All Search Configs", True, f"Found configs for {entity_count} entity types")
                return True
            else:
                self.log_test("Get All Search Configs", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Search Configs", False, f"Error: {str(e)}")
            return False
    
    async def test_search_suggestions(self) -> bool:
        """Test search suggestions/autocomplete"""
        try:
            response = await self.client.get(
                f"{API_BASE}/search/suggestions",
                params={"query": "john", "entity_type": "student", "limit": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", [])
                self.log_test("Search Suggestions", True, f"Got {len(suggestions)} suggestions")
                return True
            else:
                self.log_test("Search Suggestions", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Search Suggestions", False, f"Error: {str(e)}")
            return False
    
    async def test_popular_searches(self) -> bool:
        """Test getting popular searches"""
        try:
            response = await self.client.get(
                f"{API_BASE}/search/popular",
                params={"days": 7, "limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                popular_searches = data.get("popular_searches", [])
                self.log_test("Popular Searches", True, f"Found {len(popular_searches)} popular searches")
                return True
            else:
                self.log_test("Popular Searches", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Popular Searches", False, f"Error: {str(e)}")
            return False
    
    async def test_search_statistics(self) -> bool:
        """Test getting search statistics"""
        try:
            response = await self.client.get(f"{API_BASE}/search/statistics")
            
            if response.status_code == 200:
                data = response.json()
                total_searches = data.get("total_searches", 0)
                self.log_test("Search Statistics", True, f"Total searches: {total_searches}")
                return True
            else:
                self.log_test("Search Statistics", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Search Statistics", False, f"Error: {str(e)}")
            return False
    
    async def test_search_logs(self) -> bool:
        """Test getting search logs"""
        try:
            response = await self.client.get(
                f"{API_BASE}/search/logs",
                params={"skip": 0, "limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                logs = data.get("logs", [])
                self.log_test("Search Logs", True, f"Retrieved {len(logs)} search logs")
                return True
            else:
                self.log_test("Search Logs", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Search Logs", False, f"Error: {str(e)}")
            return False
    
    async def test_rebuild_search_index(self) -> bool:
        """Test rebuilding search index"""
        try:
            response = await self.client.post(
                f"{API_BASE}/search/index/rebuild",
                params={"entity_type": "student"}
            )
            
            if response.status_code == 200:
                data = response.json()
                indexed_count = data.get("indexed_count", 0)
                self.log_test("Rebuild Search Index", True, f"Indexed {indexed_count} entities")
                return True
            else:
                self.log_test("Rebuild Search Index", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Rebuild Search Index", False, f"Error: {str(e)}")
            return False
    
    async def test_create_search_index(self) -> bool:
        """Test creating a search index"""
        try:
            index_request = {
                "entity_type": "student",
                "entity_id": 1,
                "searchable_text": "John Doe student active",
                "metadata": {
                    "class_name": "Form 1A",
                    "status": "active"
                }
            }
            
            response = await self.client.post(
                f"{API_BASE}/search/index",
                json=index_request
            )
            
            if response.status_code == 200:
                self.log_test("Create Search Index", True, "Search index created successfully")
                return True
            else:
                self.log_test("Create Search Index", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create Search Index", False, f"Error: {str(e)}")
            return False
    
    async def test_delete_search_index(self) -> bool:
        """Test deleting a search index"""
        try:
            response = await self.client.delete(f"{API_BASE}/search/index/student/1")
            
            if response.status_code == 200:
                self.log_test("Delete Search Index", True, "Search index deleted successfully")
                return True
            else:
                self.log_test("Delete Search Index", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Delete Search Index", False, f"Error: {str(e)}")
            return False
    
    async def test_search_pagination(self) -> bool:
        """Test search pagination"""
        try:
            search_request = {
                "query": "test",
                "entity_type": "student",
                "page": 2,
                "page_size": 5
            }
            
            response = await self.client.post(
                f"{API_BASE}/search/",
                json=search_request
            )
            
            if response.status_code == 200:
                data = response.json()
                page = data.get("page", 1)
                total_pages = data.get("total_pages", 1)
                self.log_test("Search Pagination", True, f"Page {page} of {total_pages}")
                return True
            else:
                self.log_test("Search Pagination", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Search Pagination", False, f"Error: {str(e)}")
            return False
    
    async def test_search_sorting(self) -> bool:
        """Test search sorting"""
        try:
            search_request = {
                "query": "",
                "entity_type": "student",
                "sort_by": "name",
                "sort_order": "desc",
                "page": 1,
                "page_size": 10
            }
            
            response = await self.client.post(
                f"{API_BASE}/search/",
                json=search_request
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                self.log_test("Search Sorting", True, f"Sorted {len(results)} results in descending order")
                return True
            else:
                self.log_test("Search Sorting", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Search Sorting", False, f"Error: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        console.print("\n" + "="*60)
        console.print("[bold blue]SEARCH MANAGEMENT SYSTEM TEST SUMMARY[/bold blue]")
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
            console.print("\n[bold green]🎉 ALL TESTS PASSED! Search Management System is working correctly.[/bold green]")
        else:
            console.print(f"\n[bold red]⚠️  {failed_tests} test(s) failed. Please check the implementation.[/bold red]")
        
        return failed_tests == 0

async def main():
    """Main test function"""
    console.print(Panel.fit(
        "[bold blue]Search Management System Test Suite[/bold blue]\n"
        "Testing advanced search and filtering functionality...",
        border_style="blue"
    ))
    
    async with SearchManagementTester() as tester:
        # Test sequence
        tests = [
            ("Health Check", tester.test_health_check),
            ("Search Students", tester.test_search_students),
            ("Global Search", tester.test_global_search),
            ("Search with Filters", tester.test_search_with_filters),
            ("Get Search Config", tester.test_get_search_config),
            ("Get All Search Configs", tester.test_get_all_search_configs),
            ("Search Suggestions", tester.test_search_suggestions),
            ("Popular Searches", tester.test_popular_searches),
            ("Search Statistics", tester.test_search_statistics),
            ("Search Logs", tester.test_search_logs),
            ("Create Search Index", tester.test_create_search_index),
            ("Rebuild Search Index", tester.test_rebuild_search_index),
            ("Search Pagination", tester.test_search_pagination),
            ("Search Sorting", tester.test_search_sorting),
            ("Delete Search Index", tester.test_delete_search_index),
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
        results_file = f"logs/search_management_test_{timestamp}.json"
        
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