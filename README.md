# 🎓 Arusha Catholic Seminary School Management System

A comprehensive school management system with modern authentication, user management, and beautiful UI.

## 🚀 Quick Start

### Option 1: One-Command Startup (Recommended)
```bash
python start.py
```
This will start both backend and frontend automatically.

### Option 2: Manual Startup

#### Start Backend Server
```bash
cd backend
python server.py
```

#### Start Frontend Server (in a new terminal)
```bash
cd frontend
npm start
```

## 📋 System Requirements

- **Python 3.8+**
- **Node.js 16+**
- **npm 8+**

## 🔧 Installation

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies
```bash
cd frontend
npm install
```

## 🌐 Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔑 Default Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

## ✨ Features

### ✅ Authentication System
- User registration and login
- JWT token authentication
- Password reset functionality
- Profile management
- Secure password validation

### ✅ School Management
- Student management
- Teacher management
- Class management
- Role-based access control

### ✅ Modern UI
- Responsive design
- Beautiful interface
- Mobile-friendly
- Real-time updates

## 📁 Project Structure

```
arusha-catholic-seminary/
├── backend/
│   ├── server.py          # Main server file (everything in one file!)
│   ├── requirements.txt   # Python dependencies
│   └── users.json         # User data (auto-created)
├── frontend/
│   ├── src/               # React source code
│   ├── package.json       # Node.js dependencies
│   └── public/            # Static files
├── start.py              # One-command startup script
└── README.md             # This file
```

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/forgot-password` - Forgot password
- `POST /api/v1/auth/reset-password` - Reset password
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user info

### School Management
- `GET /api/v1/students` - Get all students
- `GET /api/v1/teachers` - Get all teachers
- `GET /api/v1/classes` - Get all classes

## 🛠️ Development

### Backend Development
The backend is now a single file (`backend/server.py`) that contains:
- FastAPI application
- Authentication system
- Database models
- API endpoints
- Utility functions

### Frontend Development
The frontend is a React application with:
- Modern UI components
- State management
- API integration
- Responsive design

## 🐛 Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Find and kill the process
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Port 3000 already in use**
   ```bash
   # Find and kill the process
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F
   ```

3. **Python dependencies missing**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Node.js dependencies missing**
   ```bash
   cd frontend
   npm install
   ```

### Network Error Solutions
If you get network errors when clicking "Sign In":
1. Make sure the backend server is running on port 8000
2. Check that CORS is properly configured
3. Verify the frontend is connecting to the correct backend URL

## 📝 License

This project is for educational purposes.

## 🤝 Support

For support or questions, please check the troubleshooting section above.

---

**🎓 Arusha Catholic Seminary School Management System** - Making education management simple and efficient! 