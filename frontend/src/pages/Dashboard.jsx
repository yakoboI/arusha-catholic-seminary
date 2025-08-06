import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard = ({ user }) => {
  // Role-based content configuration
  const getRoleBasedContent = () => {
    const role = user?.role || 'admin';
    
    switch (role) {
      case 'admin':
        return {
          stats: [
            { name: 'Total Students', value: '1,234', change: '+12%', changeType: 'positive', href: '/students' },
            { name: 'Total Teachers', value: '45', change: '+5%', changeType: 'positive', href: '/teachers' },
            { name: 'Active Classes', value: '32', change: '+2%', changeType: 'positive', href: '/classes' },
            { name: 'Attendance Rate', value: '94%', change: '+1%', changeType: 'positive', href: '/attendance' },
          ],
          quickActions: [
            { name: 'Add Student', href: '/students', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z' },
            { name: 'Add Teacher', href: '/teachers', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
            { name: 'Create Class', href: '/classes', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
            { name: 'Generate Reports', href: '/reports', icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
          ],
          welcomeMessage: 'Here\'s what\'s happening at Arusha Catholic Seminary today.',
          title: 'Administrator Dashboard'
        };
        
      case 'teacher':
        return {
          stats: [
            { name: 'My Classes', value: '4', change: '+1', changeType: 'positive', href: '/classes' },
            { name: 'Total Students', value: '120', change: '+5', changeType: 'positive', href: '/students' },
            { name: 'Average Grade', value: 'B+', change: '+0.3', changeType: 'positive', href: '/grades' },
            { name: 'Attendance Rate', value: '96%', change: '+2%', changeType: 'positive', href: '/attendance' },
          ],
          quickActions: [
            { name: 'Mark Attendance', href: '/attendance', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
            { name: 'Update Grades', href: '/grades', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
            { name: 'View Students', href: '/students', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z' },
            { name: 'Class Reports', href: '/reports', icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
          ],
          welcomeMessage: 'Manage your classes and track student progress.',
          title: 'Teacher Dashboard'
        };
        
      case 'student':
        return {
          stats: [
            { name: 'My Classes', value: '6', change: '0', changeType: 'neutral', href: '/classes' },
            { name: 'Current GPA', value: '3.8', change: '+0.2', changeType: 'positive', href: '/grades' },
            { name: 'Attendance', value: '98%', change: '+1%', changeType: 'positive', href: '/attendance' },
            { name: 'Assignments Due', value: '3', change: '-1', changeType: 'positive', href: '/grades' },
          ],
          quickActions: [
            { name: 'View Grades', href: '/grades', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
            { name: 'Check Attendance', href: '/attendance', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
            { name: 'My Schedule', href: '/classes', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
            { name: 'Academic Reports', href: '/reports', icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
          ],
          welcomeMessage: 'Track your academic progress and stay organized.',
          title: 'Student Dashboard'
        };
        
      default:
        return {
          stats: [
            { name: 'Total Students', value: '1,234', change: '+12%', changeType: 'positive', href: '/students' },
            { name: 'Total Teachers', value: '45', change: '+5%', changeType: 'positive', href: '/teachers' },
            { name: 'Active Classes', value: '32', change: '+2%', changeType: 'positive', href: '/classes' },
            { name: 'Attendance Rate', value: '94%', change: '+1%', changeType: 'positive', href: '/attendance' },
          ],
          quickActions: [
            { name: 'View Students', href: '/students', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z' },
            { name: 'View Teachers', href: '/teachers', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
            { name: 'View Classes', href: '/classes', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
            { name: 'View Reports', href: '/reports', icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
          ],
          welcomeMessage: 'Welcome to Arusha Catholic Seminary.',
          title: 'Dashboard'
        };
    }
  };

  const { stats, quickActions, welcomeMessage, title } = getRoleBasedContent();

  const recentActivities = [
    { id: 1, type: 'student', action: 'New student registered', name: 'John Doe', time: '2 hours ago' },
    { id: 2, type: 'grade', action: 'Grades updated', name: 'Class 10A', time: '4 hours ago' },
    { id: 3, type: 'attendance', action: 'Attendance marked', name: 'Class 9B', time: '6 hours ago' },
    { id: 4, type: 'teacher', action: 'New teacher assigned', name: 'Mrs. Smith', time: '1 day ago' },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">
              {title}
            </h1>
            <p className="text-secondary-600 mt-1">
              Welcome back, {user?.full_name?.split(' ')[0] || 'User'}! {welcomeMessage}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-secondary-500">Today</p>
            <p className="text-lg font-semibold text-secondary-900">
              {new Date().toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white overflow-hidden shadow-sm rounded-lg border border-secondary-200">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-1">
                  <dt className="text-sm font-medium text-secondary-500 truncate">{stat.name}</dt>
                  <dd className="mt-1 text-3xl font-semibold text-secondary-900">{stat.value}</dd>
                </div>
                <div className={`flex items-baseline text-sm font-semibold ${
                  stat.changeType === 'positive' ? 'text-green-600' : 
                  stat.changeType === 'negative' ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {stat.change}
                </div>
              </div>
              <div className="mt-4">
                <Link
                  to={stat.href}
                  className="text-sm font-medium text-primary-600 hover:text-primary-500"
                >
                  View details →
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Quick Actions */}
        <div className="bg-white shadow-sm rounded-lg border border-secondary-200">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-secondary-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-4">
              {quickActions.map((action) => (
                <Link
                  key={action.name}
                  to={action.href}
                  className="group relative rounded-lg p-4 border border-secondary-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
                >
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg
                        className="h-6 w-6 text-secondary-400 group-hover:text-primary-500"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={action.icon} />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-secondary-900 group-hover:text-primary-900">
                        {action.name}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activities */}
        <div className="bg-white shadow-sm rounded-lg border border-secondary-200">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-secondary-900 mb-4">Recent Activities</h3>
            <div className="flow-root">
              <ul className="-mb-8">
                {recentActivities.map((activity, activityIdx) => (
                  <li key={activity.id}>
                    <div className="relative pb-8">
                      {activityIdx !== recentActivities.length - 1 ? (
                        <span
                          className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-secondary-200"
                          aria-hidden="true"
                        />
                      ) : null}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                            activity.type === 'student' ? 'bg-blue-500' :
                            activity.type === 'grade' ? 'bg-green-500' :
                            activity.type === 'attendance' ? 'bg-yellow-500' :
                            'bg-purple-500'
                          }`}>
                            <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                            </svg>
                          </span>
                        </div>
                        <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                          <div>
                            <p className="text-sm text-secondary-500">
                              {activity.action} <span className="font-medium text-secondary-900">{activity.name}</span>
                            </p>
                          </div>
                          <div className="text-right text-sm whitespace-nowrap text-secondary-500">
                            <time>{activity.time}</time>
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 