import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { FeedbackProvider } from './contexts/FeedbackContext';
import useAuthStore from './stores/useAuthStore';
import ResponsiveLayout from './components/ResponsiveLayout';
import LoginForm from './components/LoginForm';
import LoginTest from './components/LoginTest';
import RegisterForm from './components/RegisterForm';
import ForgotPasswordForm from './components/ForgotPasswordForm';
import ResetPasswordForm from './components/ResetPasswordForm';
import DashboardLayout from './components/DashboardLayout';
import Dashboard from './pages/Dashboard';

// Import pages
import Students from './pages/Students';
import Teachers from './pages/Teachers';
import Classes from './pages/Classes';
import Grades from './pages/Grades';
import Attendance from './pages/Attendance';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import Profile from './pages/Profile';
import Alumni from './pages/Alumni';
import ARUCASER from './pages/ARUCASER';
import Donors from './pages/Donors';
import Parents from './pages/Parents';
import NonTeachingStaff from './pages/NonTeachingStaff';

// Import mobile styles
import './styles/mobile.css';

function App() {
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
  };

  // Protected Route component
  const ProtectedRoute = ({ children }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }
    return children;
  };

  // Public Route component (redirects to dashboard if already authenticated)
  const PublicRoute = ({ children }) => {
    if (isAuthenticated) {
      return <Navigate to="/dashboard" replace />;
    }
    return children;
  };

  return (
    <FeedbackProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Test Route - Remove this after testing */}
            <Route 
              path="/test-login" 
              element={<LoginTest />} 
            />

            {/* Public Routes */}
            <Route 
              path="/login" 
              element={
                <PublicRoute>
                  <LoginForm />
                </PublicRoute>
              } 
            />

            <Route 
              path="/register" 
              element={
                <PublicRoute>
                  <RegisterForm />
                </PublicRoute>
              } 
            />

            <Route 
              path="/forgot-password" 
              element={
                <PublicRoute>
                  <ForgotPasswordForm />
                </PublicRoute>
              } 
            />

            <Route 
              path="/reset-password" 
              element={
                <PublicRoute>
                  <ResetPasswordForm />
                </PublicRoute>
              } 
            />

            {/* Root redirect to dashboard */}
            <Route 
              path="/" 
              element={<Navigate to="/dashboard" replace />} 
            />

            {/* Protected Dashboard and Pages */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Dashboard user={user} />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            {/* Role-based routes */}
            <Route 
              path="/:role/dashboard" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Dashboard user={user} />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/students" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Students />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/students" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Students />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/teachers" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Teachers />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/teachers" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Teachers />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/classes" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Classes />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/classes" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Classes />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/grades" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Grades />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/grades" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Grades />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/attendance" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Attendance />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/attendance" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Attendance />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/reports" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Reports />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/reports" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Reports />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Settings />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/settings" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Settings />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Profile />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/profile" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Profile />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/alumni" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Alumni />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/alumni" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Alumni />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/arucaser" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <ARUCASER />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/arucaser" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <ARUCASER />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/donors" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Donors />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/donors" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Donors />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/parents" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Parents />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/parents" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <Parents />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/non-teaching-staff" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <NonTeachingStaff />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/:role/non-teaching-staff" 
              element={
                <ProtectedRoute>
                  <ResponsiveLayout user={user} onLogout={handleLogout}>
                    <DashboardLayout user={user}>
                      <NonTeachingStaff />
                    </DashboardLayout>
                  </ResponsiveLayout>
                </ProtectedRoute>
              } 
            />

            {/* Catch all route - redirect to dashboard */}
            <Route 
              path="*" 
              element={<Navigate to="/dashboard" replace />} 
            />
          </Routes>
        </div>
      </Router>
    </FeedbackProvider>
  );
}

export default App; 