import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import MobileNavigation from './MobileNavigation';
import MobileBottomNavigation from './MobileBottomNavigation';
import ResponsiveDashboard from './ResponsiveDashboard';

const ResponsiveLayout = ({ 
  children, 
  user, 
  onLogout,
  showBottomNav = true,
  showMobileNav = true,
  className = ''
}) => {
  const location = useLocation();
  const [isMobile, setIsMobile] = useState(false);

  // Check if current route should show bottom navigation
  const shouldShowBottomNav = () => {
    const routesWithBottomNav = ['/', '/students', '/teachers', '/classes', '/grades', '/attendance', '/reports'];
    return routesWithBottomNav.some(route => location.pathname.startsWith(route));
  };

  // Check if current route should show mobile navigation
  const shouldShowMobileNav = () => {
    const routesWithoutMobileNav = ['/login', '/register', '/forgot-password', '/reset-password'];
    return !routesWithoutMobileNav.some(route => location.pathname.startsWith(route));
  };

  // Handle window resize
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024); // lg breakpoint
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Add bottom padding for mobile bottom navigation
  const getBottomPadding = () => {
    if (isMobile && showBottomNav && shouldShowBottomNav()) {
      return 'pb-20'; // Space for bottom navigation
    }
    return '';
  };

  // Check if current page is dashboard
  const isDashboard = location.pathname === '/';

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Mobile Navigation */}
      {showMobileNav && shouldShowMobileNav() && (
        <MobileNavigation user={user} onLogout={onLogout} />
      )}

      {/* Main Content */}
      <div className={`${getBottomPadding()}`}>
        {/* Dashboard with responsive layout */}
        {isDashboard ? (
          <ResponsiveDashboard 
            stats={[
              { title: 'Total Students', value: '1,234', change: '+12%', icon: 'Users', color: 'blue' },
              { title: 'Teachers', value: '45', change: '+5%', icon: 'GraduationCap', color: 'green' },
              { title: 'Classes', value: '32', change: '+2%', icon: 'BookOpen', color: 'purple' },
              { title: 'Attendance', value: '94%', change: '+3%', icon: 'Calendar', color: 'orange' }
            ]}
            recentActivities={[
              {
                title: 'New student registered',
                description: 'John Doe has been added to Class 10A',
                time: '2 hours ago'
              },
              {
                title: 'Attendance recorded',
                description: 'Daily attendance has been recorded for all classes',
                time: '4 hours ago'
              },
              {
                title: 'Grade updated',
                description: 'Mathematics grades have been updated for Class 9B',
                time: '6 hours ago'
              }
            ]}
            notifications={[
              {
                title: 'System Update',
                message: 'New features have been added to the system',
                time: '1 hour ago'
              },
              {
                title: 'Attendance Alert',
                message: 'Low attendance detected in Class 8A',
                time: '3 hours ago'
              }
            ]}
            onQuickAction={(action) => {
              console.log('Quick action:', action);
              // Handle quick actions
            }}
            onViewAll={(section) => {
              console.log('View all:', section);
              // Handle view all actions
            }}
          />
        ) : (
          // Other pages with standard responsive layout
          <div className="p-4 lg:p-6">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </div>
        )}
      </div>

      {/* Mobile Bottom Navigation */}
      {showBottomNav && shouldShowBottomNav() && (
        <MobileBottomNavigation />
      )}

      {/* Mobile-specific styles */}
      <style jsx>{`
        @media (max-width: 1023px) {
          /* Ensure content doesn't overlap with bottom navigation */
          .pb-20 {
            padding-bottom: 5rem;
          }
        }
        
        /* Touch-friendly button sizes for mobile */
        @media (max-width: 768px) {
          button, [role="button"] {
            min-height: 44px;
            min-width: 44px;
          }
          
          input, select, textarea {
            font-size: 16px; /* Prevents zoom on iOS */
          }
        }
        
        /* Smooth scrolling for mobile */
        html {
          scroll-behavior: smooth;
        }
        
        /* Prevent horizontal scroll on mobile */
        body {
          overflow-x: hidden;
        }
      `}</style>
    </div>
  );
};

// Responsive wrapper components
export const ResponsiveContainer = ({ children, className = '' }) => {
  return (
    <div className={`w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
};

export const ResponsiveGrid = ({ children, cols = 1, className = '' }) => {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
    6: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-6'
  };

  return (
    <div className={`grid gap-4 lg:gap-6 ${gridCols[cols]} ${className}`}>
      {children}
    </div>
  );
};

export const ResponsiveCard = ({ children, className = '' }) => {
  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 lg:p-6 ${className}`}>
      {children}
    </div>
  );
};

export const ResponsiveSection = ({ title, children, className = '' }) => {
  return (
    <section className={`space-y-4 lg:space-y-6 ${className}`}>
      {title && (
        <div className="flex items-center justify-between">
          <h2 className="text-lg lg:text-xl font-semibold text-gray-900">{title}</h2>
        </div>
      )}
      {children}
    </section>
  );
};

export const ResponsiveButton = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  className = '',
  ...props 
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500'
  };
  
  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm lg:text-base',
    lg: 'px-6 py-3 text-base lg:text-lg'
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default ResponsiveLayout; 