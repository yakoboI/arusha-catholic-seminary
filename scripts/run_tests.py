#!/usr/bin/env python3
"""
Comprehensive Test Runner for Arusha Catholic Seminary
Runs backend and frontend tests with coverage and reporting
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

def run_command(command, cwd=None, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def run_backend_tests(args):
    """Run backend tests"""
    print("🔧 Running Backend Tests...")
    print("=" * 50)
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Install dependencies if needed
    if args.install_deps:
        print("📦 Installing backend dependencies...")
        result = run_command("pip install -r requirements.txt")
        if not result:
            return False
    
    # Run tests based on arguments
    test_command = "pytest"
    
    if args.unit:
        test_command += " -m unit"
    elif args.integration:
        test_command += " -m integration"
    elif args.auth:
        test_command += " -m auth"
    elif args.students:
        test_command += " -m students"
    elif args.teachers:
        test_command += " -m teachers"
    elif args.classes:
        test_command += " -m classes"
    elif args.grades:
        test_command += " -m grades"
    elif args.slow:
        test_command += " -m slow"
    else:
        # Run all tests
        pass
    
    if args.verbose:
        test_command += " -v"
    
    if args.coverage:
        test_command += " --cov=app --cov-report=term-missing --cov-report=html:htmlcov"
    
    if args.watch:
        test_command += " --watch"
    
    print(f"Running: {test_command}")
    result = run_command(test_command)
    
    if result:
        print("✅ Backend tests completed successfully!")
        return True
    else:
        print("❌ Backend tests failed!")
        return False

def run_frontend_tests(args):
    """Run frontend tests"""
    print("🎨 Running Frontend Tests...")
    print("=" * 50)
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Install dependencies if needed
    if args.install_deps:
        print("📦 Installing frontend dependencies...")
        result = run_command("npm install")
        if not result:
            return False
    
    # Run tests
    test_command = "npm test"
    
    if args.watch:
        test_command += " -- --watch"
    
    if args.coverage:
        test_command += " -- --coverage --watchAll=false"
    
    print(f"Running: {test_command}")
    result = run_command(test_command)
    
    if result:
        print("✅ Frontend tests completed successfully!")
        return True
    else:
        print("❌ Frontend tests failed!")
        return False

def run_e2e_tests(args):
    """Run end-to-end tests"""
    print("🌐 Running End-to-End Tests...")
    print("=" * 50)
    
    # This would run Cypress or Playwright tests
    # For now, just a placeholder
    print("⚠️  E2E tests not yet implemented")
    return True

def generate_test_report():
    """Generate a comprehensive test report"""
    print("📊 Generating Test Report...")
    print("=" * 50)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "backend": {
            "coverage": "htmlcov/index.html",
            "results": "test-results.xml"
        },
        "frontend": {
            "coverage": "coverage/lcov-report/index.html",
            "results": "test-results.xml"
        }
    }
    
    print("📈 Test Report Generated:")
    print(f"   Backend Coverage: {report['backend']['coverage']}")
    print(f"   Frontend Coverage: {report['frontend']['coverage']}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Run tests for Arusha Catholic Seminary")
    parser.add_argument("--backend", action="store_true", help="Run backend tests only")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests only")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies before testing")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage reports")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--watch", action="store_true", help="Watch mode for tests")
    
    # Backend test options
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--auth", action="store_true", help="Run authentication tests only")
    parser.add_argument("--students", action="store_true", help="Run student management tests only")
    parser.add_argument("--teachers", action="store_true", help="Run teacher management tests only")
    parser.add_argument("--classes", action="store_true", help="Run class management tests only")
    parser.add_argument("--grades", action="store_true", help="Run grade management tests only")
    parser.add_argument("--slow", action="store_true", help="Run slow tests only")
    
    args = parser.parse_args()
    
    # Store original directory
    original_dir = os.getcwd()
    
    try:
        success = True
        
        if args.all or (not args.backend and not args.frontend and not args.e2e):
            # Run all tests
            print("🚀 Running All Tests")
            print("=" * 60)
            
            success &= run_backend_tests(args)
            success &= run_frontend_tests(args)
            success &= run_e2e_tests(args)
            
        else:
            if args.backend:
                success &= run_backend_tests(args)
            
            if args.frontend:
                success &= run_frontend_tests(args)
            
            if args.e2e:
                success &= run_e2e_tests(args)
        
        # Generate report if coverage was requested
        if args.coverage:
            generate_test_report()
        
        # Return to original directory
        os.chdir(original_dir)
        
        if success:
            print("\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        os.chdir(original_dir)
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        os.chdir(original_dir)
        sys.exit(1)

if __name__ == "__main__":
    main() 