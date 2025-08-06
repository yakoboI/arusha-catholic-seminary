import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Users, 
  BookOpen, 
  FileText, 
  MoreHorizontal 
} from 'lucide-react';

const MobileBottomNavigation = () => {
  const location = useLocation();

  const navigationItems = [
    { name: 'Dashboard', path: '/', icon: Home },
    { name: 'Students', path: '/students', icon: Users },
    { name: 'Classes', path: '/classes', icon: BookOpen },
    { name: 'Reports', path: '/reports', icon: FileText },
    { name: 'More', path: '/more', icon: MoreHorizontal }
  ];

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200">
      <div className="flex items-center justify-around px-2 py-2">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex flex-col items-center justify-center py-2 px-3 rounded-lg transition-colors ${
                active
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Icon size={20} />
              <span className="text-xs font-medium mt-1">{item.name}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

export default MobileBottomNavigation; 