import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { apiUtils } from '../services/api';
import toast from 'react-hot-toast';
import Dashboard from '../pages/Dashboard';

const DashboardLayout = ({ children, user }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    apiUtils.clearAuth();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  const navigation = [
    {
      name: 'Dashboard',
      href: `/${user?.role || 'admin'}/dashboard`,
      icon: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z',
      current: location.pathname.includes('dashboard')
    },
    {
      name: 'Students',
      href: `/${user?.role || 'admin'}/students`,
      icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z',
      current: location.pathname.includes('students'),
      showFor: ['admin', 'teacher', 'administrator']
    },
    {
      name: 'Teachers',
      href: `/${user?.role || 'admin'}/teachers`,
      icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
      current: location.pathname.includes('teachers'),
      showFor: ['admin', 'administrator']
    },
    {
      name: 'Non-Teaching Staff',
      href: `/${user?.role || 'admin'}/non-teaching-staff`,
      icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
      current: location.pathname.includes('non-teaching-staff'),
      showFor: ['admin', 'administrator']
    },
    {
      name: 'Parents',
      href: `/${user?.role || 'admin'}/parents`,
      icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
      current: location.pathname.includes('parents'),
      showFor: ['admin', 'administrator', 'teacher']
    },
    {
      name: 'Alumni',
      href: `/${user?.role || 'admin'}/alumni`,
      icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z',
      current: location.pathname.includes('alumni'),
      showFor: ['admin', 'administrator', 'teacher']
    },
    {
      name: 'Donors',
      href: `/${user?.role || 'admin'}/donors`,
      icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1',
      current: location.pathname.includes('donors'),
      showFor: ['admin', 'administrator']
    },
    {
      name: 'Classes',
      href: `/${user?.role || 'admin'}/classes`,
      icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
      current: location.pathname.includes('classes'),
      showFor: ['admin', 'teacher', 'administrator']
    },
    {
      name: 'Grades',
      href: `/${user?.role || 'admin'}/grades`,
      icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
      current: location.pathname.includes('grades'),
      showFor: ['admin', 'teacher', 'student', 'administrator']
    },
    {
      name: 'Attendance',
      href: `/${user?.role || 'admin'}/attendance`,
      icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
      current: location.pathname.includes('attendance'),
      showFor: ['admin', 'teacher', 'student', 'administrator']
    },
    {
      name: 'Reports',
      href: `/${user?.role || 'admin'}/reports`,
      icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
      current: location.pathname.includes('reports'),
      showFor: ['admin', 'teacher', 'administrator']
    },
    {
      name: 'Settings',
      href: `/${user?.role || 'admin'}/settings`,
      icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
      current: location.pathname.includes('settings'),
      showFor: ['admin', 'teacher', 'student', 'administrator']
    }
  ];

  // Filter navigation items based on user role
  const filteredNavigation = navigation.filter(item => {
    // Admin users can see everything
    if (user?.role === 'admin' || user?.role === 'administrator') {
      return true;
    }
    // For other users, check if they have permission
    if (item.showFor) {
      return item.showFor.includes(user?.role);
    }
    return true;
  });

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-secondary-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white">
          <div className="flex h-16 items-center justify-between px-4">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-primary-600">Arusha Seminary</h1>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-secondary-400 hover:text-secondary-600"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4">
            {filteredNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  item.current
                    ? 'bg-primary-100 text-primary-900'
                    : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <svg
                  className={`mr-3 h-6 w-6 flex-shrink-0 ${
                    item.current ? 'text-primary-500' : 'text-secondary-400 group-hover:text-secondary-500'
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                </svg>
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r border-secondary-200">
          <div className="flex h-16 items-center px-4 border-b border-secondary-200">
            <h1 className="text-xl font-bold text-primary-600">Arusha Seminary</h1>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4">
            {filteredNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  item.current
                    ? 'bg-primary-100 text-primary-900'
                    : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
                }`}
              >
                <svg
                  className={`mr-3 h-6 w-6 flex-shrink-0 ${
                    item.current ? 'text-primary-500' : 'text-secondary-400 group-hover:text-secondary-500'
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                </svg>
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-secondary-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-secondary-700 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="sr-only">Open sidebar</span>
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1"></div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              {/* User menu */}
              <div className="relative">
                <div className="flex items-center space-x-3">
                  <div className="text-right">
                    <p className="text-sm font-medium text-secondary-900">{user?.full_name}</p>
                    <p className="text-xs text-secondary-500 capitalize">{user?.role}</p>
                  </div>
                  <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                    <span className="text-sm font-medium text-primary-600">
                      {user?.full_name?.charAt(0)?.toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Logout button */}
              <button
                onClick={handleLogout}
                className="text-secondary-400 hover:text-secondary-600"
                title="Logout"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children || <Dashboard user={user} />}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout; 