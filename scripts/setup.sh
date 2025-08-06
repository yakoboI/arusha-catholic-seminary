#!/bin/bash

# =============================================================================
# Arusha Catholic Seminary - Project Setup Script
# =============================================================================
# This script sets up the development environment for the project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION="3.8"
        
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python $PYTHON_VERSION found (>= $REQUIRED_VERSION)"
        else
            print_error "Python $PYTHON_VERSION found, but $REQUIRED_VERSION or higher is required"
            exit 1
        fi
    else
        print_error "Python 3.8 or higher is required but not installed"
        exit 1
    fi
}

# Function to check Node.js version
check_node_version() {
    if command_exists node; then
        NODE_VERSION=$(node -v | cut -d'v' -f2)
        REQUIRED_VERSION="16"
        
        if node -e "process.exit(process.version.split('v')[1].split('.')[0] >= $REQUIRED_VERSION ? 0 : 1)"; then
            print_success "Node.js $NODE_VERSION found (>= $REQUIRED_VERSION)"
        else
            print_error "Node.js $NODE_VERSION found, but $REQUIRED_VERSION or higher is required"
            exit 1
        fi
    else
        print_error "Node.js 16 or higher is required but not installed"
        exit 1
    fi
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create necessary directories
    print_status "Creating necessary directories..."
    mkdir -p uploads logs backups database
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp ../env.example .env
        print_warning "Please update .env file with your configuration"
    fi
    
    # Initialize database
    print_status "Initializing database..."
    python -c "
import sys
sys.path.append('.')
from app.database import create_tables, migrate_database
from main import app
create_tables()
migrate_database()
print('Database initialized successfully')
"
    
    print_success "Backend setup completed"
    cd ..
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_warning "Please update .env file with your configuration"
    fi
    
    print_success "Frontend setup completed"
    cd ..
}

# Function to setup Docker (optional)
setup_docker() {
    if command_exists docker && command_exists docker-compose; then
        print_status "Setting up Docker environment..."
        
        # Create .env file for Docker if it doesn't exist
        if [ ! -f ".env" ]; then
            print_status "Creating .env file for Docker..."
            cp env.example .env
        fi
        
        print_success "Docker environment ready"
        print_status "To start with Docker, run: docker-compose up -d"
    else
        print_warning "Docker not found. Skipping Docker setup."
        print_status "To install Docker, visit: https://docs.docker.com/get-docker/"
    fi
}

# Function to create development scripts
create_dev_scripts() {
    print_status "Creating development scripts..."
    
    # Backend start script
    cat > scripts/start_backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF
    
    # Frontend start script
    cat > scripts/start_frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm start
EOF
    
    # Full start script
    cat > scripts/start_dev.sh << 'EOF'
#!/bin/bash
# Start both backend and frontend in development mode
echo "Starting Arusha Catholic Seminary in development mode..."

# Start backend in background
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "Development servers started:"
echo "Backend: http://localhost:8000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait
EOF
    
    # Make scripts executable
    chmod +x scripts/start_backend.sh
    chmod +x scripts/start_frontend.sh
    chmod +x scripts/start_dev.sh
    
    print_success "Development scripts created"
}

# Function to display next steps
show_next_steps() {
    echo ""
    echo "============================================================================="
    echo "🎉 SETUP COMPLETED SUCCESSFULLY!"
    echo "============================================================================="
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. 📝 Update configuration files:"
    echo "   - backend/.env"
    echo "   - frontend/.env"
    echo ""
    echo "2. 🚀 Start development servers:"
    echo "   - Backend only: ./scripts/start_backend.sh"
    echo "   - Frontend only: ./scripts/start_frontend.sh"
    echo "   - Both: ./scripts/start_dev.sh"
    echo ""
    echo "3. 🌐 Access the application:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "4. 🔐 Default login credentials:"
    echo "   - Username: admin"
    echo "   - Password: admin123"
    echo ""
    echo "5. 📚 Documentation:"
    echo "   - README.md - Project overview and setup"
    echo "   - TODO.md - Development roadmap"
    echo ""
    echo "============================================================================="
}

# Main setup function
main() {
    echo "============================================================================="
    echo "🏫 Arusha Catholic Seminary - Development Environment Setup"
    echo "============================================================================="
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    check_python_version
    check_node_version
    
    # Create scripts directory if it doesn't exist
    mkdir -p scripts
    
    # Setup backend
    setup_backend
    
    # Setup frontend
    setup_frontend
    
    # Setup Docker (optional)
    setup_docker
    
    # Create development scripts
    create_dev_scripts
    
    # Show next steps
    show_next_steps
}

# Run main function
main "$@" 