import React from 'react';
import { 
  Users, 
  GraduationCap, 
  BookOpen, 
  FileText, 
  TrendingUp, 
  Calendar,
  Bell,
  Search,
  Plus,
  Filter
} from 'lucide-react';

const ResponsiveDashboard = ({ 
  stats = [],
  recentActivities = [],
  quickActions = [],
  notifications = [],
  onQuickAction,
  onViewAll,
  loading = false
}) => {
  const defaultStats = [
    { title: 'Total Students', value: '1,234', change: '+12%', icon: Users, color: 'blue' },
    { title: 'Teachers', value: '45', change: '+5%', icon: GraduationCap, color: 'green' },
    { title: 'Classes', value: '32', change: '+2%', icon: BookOpen, color: 'purple' },
    { title: 'Attendance', value: '94%', change: '+3%', icon: Calendar, color: 'orange' }
  ];

  const defaultQuickActions = [
    { title: 'Add Student', icon: Plus, action: 'add-student', color: 'blue' },
    { title: 'Record Attendance', icon: Calendar, action: 'attendance', color: 'green' },
    { title: 'Generate Report', icon: FileText, action: 'report', color: 'purple' },
    { title: 'Send Notification', icon: Bell, action: 'notification', color: 'orange' }
  ];

  const displayStats = stats.length > 0 ? stats : defaultStats;
  const displayActions = quickActions.length > 0 ? quickActions : defaultQuickActions;

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 text-blue-600 border-blue-200',
      green: 'bg-green-50 text-green-600 border-green-200',
      purple: 'bg-purple-50 text-purple-600 border-purple-200',
      orange: 'bg-orange-50 text-orange-600 border-orange-200',
      red: 'bg-red-50 text-red-600 border-red-200',
      yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200'
    };
    return colors[color] || colors.blue;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Loading skeleton */}
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white rounded-lg shadow-sm p-6">
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header */}
      <div className="lg:hidden bg-white shadow-sm border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-sm text-gray-500">Welcome back!</p>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors">
              <Search size={20} />
            </button>
            <button className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors relative">
              <Bell size={20} />
              {notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                  {notifications.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="p-4 lg:p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Desktop Header */}
          <div className="hidden lg:block">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-600 mt-1">Welcome back! Here's what's happening today.</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search..."
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                </div>
                <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  <Plus size={16} />
                  <span>Quick Action</span>
                </button>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
            {displayStats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 lg:p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                      <p className="text-2xl lg:text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
                      {stat.change && (
                        <p className="text-sm text-green-600 mt-1 flex items-center">
                          <TrendingUp size={14} className="mr-1" />
                          {stat.change}
                        </p>
                      )}
                    </div>
                    <div className={`p-3 rounded-lg border ${getColorClasses(stat.color)}`}>
                      <Icon size={24} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Quick Actions */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 lg:p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
                  <Filter size={20} className="text-gray-400" />
                </div>
                <div className="space-y-3">
                  {displayActions.map((action, index) => {
                    const Icon = action.icon;
                    return (
                      <button
                        key={index}
                        onClick={() => onQuickAction && onQuickAction(action.action)}
                        className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors text-left"
                      >
                        <div className={`p-2 rounded-lg ${getColorClasses(action.color)}`}>
                          <Icon size={20} />
                        </div>
                        <span className="font-medium text-gray-700">{action.title}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Recent Activities */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 lg:p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Recent Activities</h2>
                  {onViewAll && (
                    <button
                      onClick={() => onViewAll('activities')}
                      className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                      View All
                    </button>
                  )}
                </div>
                <div className="space-y-4">
                  {recentActivities.length > 0 ? (
                    recentActivities.map((activity, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <Users size={16} className="text-blue-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                          <p className="text-sm text-gray-500">{activity.description}</p>
                          <p className="text-xs text-gray-400 mt-1">{activity.time}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <FileText size={24} className="text-gray-400" />
                      </div>
                      <p className="text-gray-500">No recent activities</p>
                      <p className="text-sm text-gray-400">Activities will appear here</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Notifications Section (Mobile) */}
          {notifications.length > 0 && (
            <div className="lg:hidden">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Notifications</h2>
                  <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                    Mark all read
                  </button>
                </div>
                <div className="space-y-3">
                  {notifications.slice(0, 3).map((notification, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-blue-50 border border-blue-200">
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{notification.title}</p>
                        <p className="text-sm text-gray-600">{notification.message}</p>
                        <p className="text-xs text-gray-400 mt-1">{notification.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Charts Section (Desktop) */}
          <div className="hidden lg:block">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Attendance Overview</h3>
                <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Chart placeholder</p>
                </div>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Grade Distribution</h3>
                <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Chart placeholder</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResponsiveDashboard; 