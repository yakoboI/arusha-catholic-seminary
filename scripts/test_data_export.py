#!/usr/bin/env python3
"""
Data Export System Test Script

This script tests the data export functionality including:
- Export job creation and management
- Export template management
- File generation in multiple formats
- Export configuration and statistics
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
TEST_EXPORT_REQUEST = {
    "name": "Test Student Export",
    "description": "Export of student data for testing",
    "entity_type": "student",
    "export_format": "csv",
    "filters": {
        "status": "active"
    },
    "columns": ["student_id", "full_name", "class_name", "status"]
}

TEST_TEMPLATE_REQUEST = {
    "name": "Student CSV Template",
    "description": "Default template for student CSV exports",
    "entity_type": "student",
    "export_format": "csv",
    "columns": ["student_id", "full_name", "class_name", "status"],
    "filters": {"status": "active"},
    "sorting": {"field": "full_name", "order": "asc"},
    "is_default": True
}

class DataExportTester:
    """Test data export functionality"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.test_results = []
        self.export_job_id = None
        self.template_id = None
        
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
    
    async def test_get_export_config(self) -> bool:
        """Test getting export configuration"""
        try:
            response = await self.client.get(f"{API_BASE}/export/config/student")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Export Config", True, f"Config for student entity with {len(data.get('available_columns', []))} columns")
                return True
            else:
                self.log_test("Get Export Config", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Export Config", False, f"Error: {str(e)}")
            return False
    
    async def test_get_all_export_configs(self) -> bool:
        """Test getting all export configurations"""
        try:
            response = await self.client.get(f"{API_BASE}/export/config")
            
            if response.status_code == 200:
                data = response.json()
                entity_count = len(data)
                self.log_test("Get All Export Configs", True, f"Found configs for {entity_count} entity types")
                return True
            else:
                self.log_test("Get All Export Configs", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Export Configs", False, f"Error: {str(e)}")
            return False
    
    async def test_create_export_template(self) -> bool:
        """Test creating an export template"""
        try:
            response = await self.client.post(
                f"{API_BASE}/export/templates",
                json=TEST_TEMPLATE_REQUEST
            )
            
            if response.status_code == 200:
                data = response.json()
                self.template_id = data["id"]
                self.log_test("Create Export Template", True, f"Template created with ID: {self.template_id}")
                return True
            else:
                self.log_test("Create Export Template", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Export Template", False, f"Error: {str(e)}")
            return False
    
    async def test_get_export_templates(self) -> bool:
        """Test getting export templates"""
        try:
            response = await self.client.get(f"{API_BASE}/export/templates")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Export Templates", True, f"Found {len(data)} templates")
                return True
            else:
                self.log_test("Get Export Templates", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Export Templates", False, f"Error: {str(e)}")
            return False
    
    async def test_create_export_job(self) -> bool:
        """Test creating an export job"""
        try:
            response = await self.client.post(
                f"{API_BASE}/export/jobs",
                json=TEST_EXPORT_REQUEST
            )
            
            if response.status_code == 200:
                data = response.json()
                self.export_job_id = data["id"]
                self.log_test("Create Export Job", True, f"Job created with ID: {self.export_job_id}")
                return True
            else:
                self.log_test("Create Export Job", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Export Job", False, f"Error: {str(e)}")
            return False
    
    async def test_get_export_jobs(self) -> bool:
        """Test getting export jobs"""
        try:
            response = await self.client.get(f"{API_BASE}/export/jobs")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Export Jobs", True, f"Found {len(data)} export jobs")
                return True
            else:
                self.log_test("Get Export Jobs", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Export Jobs", False, f"Error: {str(e)}")
            return False
    
    async def test_get_export_job_by_id(self) -> bool:
        """Test getting export job by ID"""
        if not self.export_job_id:
            self.log_test("Get Export Job by ID", False, "No export job ID available")
            return False
        
        try:
            response = await self.client.get(f"{API_BASE}/export/jobs/{self.export_job_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data["status"]
                self.log_test("Get Export Job by ID", True, f"Job status: {status}")
                return True
            else:
                self.log_test("Get Export Job by ID", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Export Job by ID", False, f"Error: {str(e)}")
            return False
    
    async def test_wait_for_export_completion(self) -> bool:
        """Wait for export job to complete"""
        if not self.export_job_id:
            self.log_test("Wait for Export Completion", False, "No export job ID available")
            return False
        
        try:
            max_wait_time = 60  # 60 seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                response = await self.client.get(f"{API_BASE}/export/jobs/{self.export_job_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    status = data["status"]
                    
                    if status == "completed":
                        self.log_test("Wait for Export Completion", True, f"Export completed in {time.time() - start_time:.1f}s")
                        return True
                    elif status == "failed":
                        self.log_test("Wait for Export Completion", False, f"Export failed: {data.get('error_message', 'Unknown error')}")
                        return False
                    elif status == "cancelled":
                        self.log_test("Wait for Export Completion", False, "Export was cancelled")
                        return False
                    
                    # Wait before checking again
                    await asyncio.sleep(2)
                else:
                    self.log_test("Wait for Export Completion", False, f"Failed to check job status: {response.status_code}")
                    return False
            
            self.log_test("Wait for Export Completion", False, "Export timed out")
            return False
            
        except Exception as e:
            self.log_test("Wait for Export Completion", False, f"Error: {str(e)}")
            return False
    
    async def test_download_export_file(self) -> bool:
        """Test downloading export file"""
        if not self.export_job_id:
            self.log_test("Download Export File", False, "No export job ID available")
            return False
        
        try:
            response = await self.client.get(f"{API_BASE}/export/jobs/{self.export_job_id}/download")
            
            if response.status_code == 200:
                content_length = len(response.content)
                self.log_test("Download Export File", True, f"File downloaded successfully ({content_length} bytes)")
                return True
            else:
                self.log_test("Download Export File", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Download Export File", False, f"Error: {str(e)}")
            return False
    
    async def test_quick_export(self) -> bool:
        """Test quick export functionality"""
        try:
            response = await self.client.post(
                f"{API_BASE}/export/quick/student",
                params={
                    "export_format": "json",
                    "columns": "student_id,full_name,status"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                record_count = data.get("record_count", 0)
                self.log_test("Quick Export", True, f"Quick export completed with {record_count} records")
                return True
            else:
                self.log_test("Quick Export", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Quick Export", False, f"Error: {str(e)}")
            return False
    
    async def test_export_different_formats(self) -> bool:
        """Test export in different formats"""
        formats = ["csv", "xlsx", "json", "xml"]
        success_count = 0
        
        for export_format in formats:
            try:
                export_request = {
                    "name": f"Test {export_format.upper()} Export",
                    "entity_type": "student",
                    "export_format": export_format,
                    "columns": ["student_id", "full_name"]
                }
                
                response = await self.client.post(
                    f"{API_BASE}/export/jobs",
                    json=export_request
                )
                
                if response.status_code == 200:
                    data = response.json()
                    job_id = data["id"]
                    
                    # Wait for completion
                    max_wait = 30
                    start_time = time.time()
                    
                    while time.time() - start_time < max_wait:
                        status_response = await self.client.get(f"{API_BASE}/export/jobs/{job_id}")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            if status_data["status"] == "completed":
                                success_count += 1
                                break
                            elif status_data["status"] in ["failed", "cancelled"]:
                                break
                        await asyncio.sleep(1)
                    
                    # Clean up
                    await self.client.delete(f"{API_BASE}/export/jobs/{job_id}")
                    
                else:
                    console.print(f"   Failed to create {export_format} export: {response.status_code}")
                    
            except Exception as e:
                console.print(f"   Error testing {export_format} export: {str(e)}")
        
        self.log_test("Export Different Formats", success_count > 0, f"Successfully tested {success_count}/{len(formats)} formats")
        return success_count > 0
    
    async def test_export_statistics(self) -> bool:
        """Test getting export statistics"""
        try:
            response = await self.client.get(f"{API_BASE}/export/statistics")
            
            if response.status_code == 200:
                data = response.json()
                total_exports = data.get("total_exports", 0)
                self.log_test("Export Statistics", True, f"Total exports: {total_exports}")
                return True
            else:
                self.log_test("Export Statistics", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Export Statistics", False, f"Error: {str(e)}")
            return False
    
    async def test_cancel_export_job(self) -> bool:
        """Test cancelling an export job"""
        try:
            # Create a new job to cancel
            response = await self.client.post(
                f"{API_BASE}/export/jobs",
                json={
                    "name": "Job to Cancel",
                    "entity_type": "student",
                    "export_format": "csv"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                job_id = data["id"]
                
                # Cancel the job
                cancel_response = await self.client.post(f"{API_BASE}/export/jobs/{job_id}/cancel")
                
                if cancel_response.status_code == 200:
                    self.log_test("Cancel Export Job", True, "Export job cancelled successfully")
                    return True
                else:
                    self.log_test("Cancel Export Job", False, f"Cancel failed: {cancel_response.status_code}")
                    return False
            else:
                self.log_test("Cancel Export Job", False, f"Failed to create job: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Cancel Export Job", False, f"Error: {str(e)}")
            return False
    
    async def test_delete_export_job(self) -> bool:
        """Test deleting an export job"""
        if not self.export_job_id:
            self.log_test("Delete Export Job", False, "No export job ID available")
            return False
        
        try:
            response = await self.client.delete(f"{API_BASE}/export/jobs/{self.export_job_id}")
            
            if response.status_code == 200:
                self.log_test("Delete Export Job", True, "Export job deleted successfully")
                self.export_job_id = None  # Clear the ID
                return True
            else:
                self.log_test("Delete Export Job", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Delete Export Job", False, f"Error: {str(e)}")
            return False
    
    async def test_delete_export_template(self) -> bool:
        """Test deleting an export template"""
        if not self.template_id:
            self.log_test("Delete Export Template", False, "No template ID available")
            return False
        
        try:
            response = await self.client.delete(f"{API_BASE}/export/templates/{self.template_id}")
            
            if response.status_code == 200:
                self.log_test("Delete Export Template", True, "Export template deleted successfully")
                self.template_id = None  # Clear the ID
                return True
            else:
                self.log_test("Delete Export Template", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Delete Export Template", False, f"Error: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        console.print("\n" + "="*60)
        console.print("[bold blue]DATA EXPORT SYSTEM TEST SUMMARY[/bold blue]")
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
            console.print("\n[bold green]🎉 ALL TESTS PASSED! Data Export System is working correctly.[/bold green]")
        else:
            console.print(f"\n[bold red]⚠️  {failed_tests} test(s) failed. Please check the implementation.[/bold red]")
        
        return failed_tests == 0

async def main():
    """Main test function"""
    console.print(Panel.fit(
        "[bold blue]Data Export System Test Suite[/bold blue]\n"
        "Testing comprehensive data export functionality...",
        border_style="blue"
    ))
    
    async with DataExportTester() as tester:
        # Test sequence
        tests = [
            ("Health Check", tester.test_health_check),
            ("Get Export Config", tester.test_get_export_config),
            ("Get All Export Configs", tester.test_get_all_export_configs),
            ("Create Export Template", tester.test_create_export_template),
            ("Get Export Templates", tester.test_get_export_templates),
            ("Create Export Job", tester.test_create_export_job),
            ("Get Export Jobs", tester.test_get_export_jobs),
            ("Get Export Job by ID", tester.test_get_export_job_by_id),
            ("Wait for Export Completion", tester.test_wait_for_export_completion),
            ("Download Export File", tester.test_download_export_file),
            ("Quick Export", tester.test_quick_export),
            ("Export Different Formats", tester.test_export_different_formats),
            ("Export Statistics", tester.test_export_statistics),
            ("Cancel Export Job", tester.test_cancel_export_job),
            ("Delete Export Job", tester.test_delete_export_job),
            ("Delete Export Template", tester.test_delete_export_template),
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
        results_file = f"logs/data_export_test_{timestamp}.json"
        
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