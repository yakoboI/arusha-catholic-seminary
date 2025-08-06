#!/usr/bin/env python3
"""
Setup script for Arusha Catholic Seminary School Management System
This script automates the initial setup process for development and deployment.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {command}")
        print(f"Error: {e.stderr}")
        return None

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "uploads",
        "logs",
        "frontend/public/assets",
        "database/migrations",
        "docs/api",
        "docs/user-guide",
        "docs/admin-guide"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def setup_backend():
    """Setup the backend environment."""
    print("\n🔧 Setting up Backend...")
    
    # Check if Python is installed
    if not shutil.which("python"):
        print("❌ Python is not installed or not in PATH")
        return False
    
    # Create virtual environment
    if not os.path.exists("backend/venv"):
        print("📦 Creating virtual environment...")
        run_command("python -m venv backend/venv")
    
    # Install dependencies
    print("📦 Installing Python dependencies...")
    if os.name == "nt":  # Windows
        run_command("backend\\venv\\Scripts\\pip install -r backend/requirements.txt")
    else:  # Unix/Linux/Mac
        run_command("backend/venv/bin/pip install -r backend/requirements.txt")
    
    return True

def setup_frontend():
    """Setup the frontend environment."""
    print("\n🎨 Setting up Frontend...")
    
    # Check if Node.js is installed
    if not shutil.which("npm"):
        print("❌ Node.js/npm is not installed or not in PATH")
        return False
    
    # Install dependencies
    print("📦 Installing Node.js dependencies...")
    run_command("npm install", cwd="frontend")
    
    return True

def setup_database():
    """Setup the database."""
    print("\n🗄️ Setting up Database...")
    
    # Check if PostgreSQL is installed
    if not shutil.which("psql"):
        print("⚠️ PostgreSQL is not installed. Please install PostgreSQL manually.")
        print("   You can use Docker instead: docker-compose up postgres")
        return False
    
    print("✅ Database setup instructions:")
    print("   1. Create a PostgreSQL database named 'arusha_seminary_db'")
    print("   2. Run the schema: psql -d arusha_seminary_db -f database/schema.sql")
    print("   3. Update the DATABASE_URL in your .env file")
    
    return True

def create_env_file():
    """Create .env file from template."""
    if not os.path.exists(".env") and os.path.exists("env.example"):
        shutil.copy("env.example", ".env")
        print("📄 Created .env file from template")
        print("⚠️ Please update the .env file with your actual configuration")

def setup_docker():
    """Setup Docker environment."""
    print("\n🐳 Setting up Docker...")
    
    if not shutil.which("docker"):
        print("⚠️ Docker is not installed. Please install Docker manually.")
        return False
    
    if not shutil.which("docker-compose"):
        print("⚠️ Docker Compose is not installed. Please install Docker Compose manually.")
        return False
    
    print("✅ Docker is available")
    print("   Run 'docker-compose up' to start all services")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Arusha Catholic Seminary School Management System Setup")
    print("=" * 60)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Setup backend
    backend_ok = setup_backend()
    
    # Setup frontend
    frontend_ok = setup_frontend()
    
    # Setup database
    database_ok = setup_database()
    
    # Setup Docker
    docker_ok = setup_docker()
    
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    
    if backend_ok:
        print("   1. Activate virtual environment:")
        if os.name == "nt":
            print("      backend\\venv\\Scripts\\activate")
        else:
            print("      source backend/venv/bin/activate")
        print("   2. Start backend: cd backend && python main.py")
    
    if frontend_ok:
        print("   3. Start frontend: cd frontend && npm start")
    
    if docker_ok:
        print("   4. Or use Docker: docker-compose up")
    
    print("\n📚 Documentation:")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Frontend: http://localhost:3000")
    print("   - Database: PostgreSQL on localhost:5432")
    
    print("\n🔧 Configuration:")
    print("   - Update .env file with your settings")
    print("   - Configure database connection")
    print("   - Set up email settings for notifications")
    
    print("\n✨ Happy coding!")

if __name__ == "__main__":
    main() 