import React, { useState, useEffect } from 'react';
import { studentAPI, teacherAPI, classAPI, gradeAPI, attendanceAPI, handleApiError } from '../services/api';
import toast from 'react-hot-toast';

const Reports = () => {
  const [students, setStudents] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [classes, setClasses] = useState([]);
  const [grades, setGrades] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState('overview');
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [studentsRes, teachersRes, classesRes, gradesRes, attendanceRes] = await Promise.all([
        studentAPI.getStudents(),
        teacherAPI.getTeachers(),
        classAPI.getClasses(),
        gradeAPI.getGrades(),
        attendanceAPI.getAttendance()
      ]);
      
      setStudents(studentsRes.success ? (studentsRes.data || []) : []);
      setTeachers(teachersRes.success ? (teachersRes.data || []) : []);
      setClasses(classesRes.success ? (classesRes.data || []) : []);
      setGrades(gradesRes.success ? (gradesRes.data || []) : []);
      setAttendance(attendanceRes.success ? (attendanceRes.data || []) : []);
    } catch (error) {
      const errorData = handleApiError(error);
      toast.error(errorData.message);
      setStudents([]);
      setTeachers([]);
      setClasses([]);
      setGrades([]);
      setAttendance([]);
    } finally {
      setLoading(false);
    }
  };

  const getOverviewStats = () => {
    if (!students || !teachers || !classes || !grades) {
      return {
        totalStudents: 0,
        totalTeachers: 0,
        totalClasses: 0,
        activeStudents: 0,
        averageGrade: 0
      };
    }
    
    const totalStudents = students.length;
    const totalTeachers = teachers.length;
    const totalClasses = classes.length;
    const activeStudents = students.filter(s => s.status === 'active').length;
    const averageGrade = grades.length > 0 
      ? grades.reduce((sum, grade) => sum + grade.total_score, 0) / grades.length 
      : 0;

    return {
      totalStudents,
      totalTeachers,
      totalClasses,
      activeStudents,
      averageGrade: Math.round(averageGrade * 100) / 100
    };
  };

  const getAttendanceStats = () => {
    if (!attendance || !Array.isArray(attendance)) {
      return { present: 0, absent: 0, late: 0, total: 0, percentage: 0 };
    }
    
    const today = new Date().toISOString().split('T')[0];
    const todayAttendance = attendance.filter(a => a.date === today);
    const present = todayAttendance.filter(a => a.status === 'present').length;
    const absent = todayAttendance.filter(a => a.status === 'absent').length;
    const late = todayAttendance.filter(a => a.status === 'late').length;
    const total = todayAttendance.length;
    const percentage = total > 0 ? Math.round((present / total) * 100) : 0;

    return { present, absent, late, total, percentage };
  };

  const getGradeDistribution = () => {
    const distribution = { A: 0, B: 0, C: 0, D: 0, F: 0 };
    if (!grades || !Array.isArray(grades)) {
      return distribution;
    }
    
    grades.forEach(grade => {
      if (distribution.hasOwnProperty(grade.grade)) {
        distribution[grade.grade]++;
      }
    });
    return distribution;
  };

  const getClassEnrollment = () => {
    const enrollment = {};
    if (!classes || !students || !Array.isArray(classes) || !Array.isArray(students)) {
      return enrollment;
    }
    
    classes.forEach(classItem => {
      const studentsInClass = students.filter(s => s.class_id === classItem.id);
      enrollment[classItem.name] = studentsInClass.length;
    });
    return enrollment;
  };

  const getTopPerformers = () => {
    if (!grades || !students || !Array.isArray(grades) || !Array.isArray(students)) {
      return [];
    }
    
    const studentGrades = {};
    grades.forEach(grade => {
      if (!studentGrades[grade.student_id]) {
        studentGrades[grade.student_id] = { total: 0, count: 0 };
      }
      studentGrades[grade.student_id].total += grade.total_score;
      studentGrades[grade.student_id].count += 1;
    });

    const averages = Object.entries(studentGrades).map(([studentId, data]) => ({
      studentId: parseInt(studentId),
      average: data.total / data.count
    }));

    return averages
      .sort((a, b) => b.average - a.average)
      .slice(0, 10)
      .map(item => {
        const student = students.find(s => s.id === item.studentId);
        return {
          name: student ? student.full_name : 'Unknown',
          average: Math.round(item.average * 100) / 100
        };
      });
  };

  const getAttendanceTrend = () => {
    const last7Days = [];
    if (!attendance || !Array.isArray(attendance)) {
      return last7Days;
    }
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const dayAttendance = attendance.filter(a => a.date === dateStr);
      const present = dayAttendance.filter(a => a.status === 'present').length;
      const total = dayAttendance.length;
      const percentage = total > 0 ? Math.round((present / total) * 100) : 0;
      
      last7Days.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        percentage
      });
    }
    return last7Days;
  };

  const stats = getOverviewStats();
  const attendanceStats = getAttendanceStats();
  const gradeDistribution = getGradeDistribution();
  const classEnrollment = getClassEnrollment();
  const topPerformers = getTopPerformers();
  const attendanceTrend = getAttendanceTrend();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Reports & Analytics</h1>
          <p className="text-secondary-600">Comprehensive insights and performance metrics</p>
        </div>
        <div className="flex space-x-4">
          <input
            type="date"
            value={dateRange.start}
            onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
            className="px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <input
            type="date"
            value={dateRange.end}
            onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
            className="px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Report Type Selector */}
      <div className="bg-white rounded-lg shadow-soft p-4">
        <div className="flex space-x-4">
          <button
            onClick={() => setSelectedReport('overview')}
            className={`px-4 py-2 rounded-lg font-medium ${
              selectedReport === 'overview'
                ? 'bg-primary-600 text-white'
                : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setSelectedReport('academic')}
            className={`px-4 py-2 rounded-lg font-medium ${
              selectedReport === 'academic'
                ? 'bg-primary-600 text-white'
                : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
            }`}
          >
            Academic Performance
          </button>
          <button
            onClick={() => setSelectedReport('attendance')}
            className={`px-4 py-2 rounded-lg font-medium ${
              selectedReport === 'attendance'
                ? 'bg-primary-600 text-white'
                : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
            }`}
          >
            Attendance
          </button>
          <button
            onClick={() => setSelectedReport('enrollment')}
            className={`px-4 py-2 rounded-lg font-medium ${
              selectedReport === 'enrollment'
                ? 'bg-primary-600 text-white'
                : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
            }`}
          >
            Enrollment
          </button>
        </div>
      </div>

      {/* Overview Report */}
      {selectedReport === 'overview' && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-soft">
              <div className="flex items-center">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Total Students</p>
                  <p className="text-2xl font-bold text-secondary-900">{stats.totalStudents}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-soft">
              <div className="flex items-center">
                <div className="p-2 bg-accent-100 rounded-lg">
                  <svg className="h-6 w-6 text-accent-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Total Teachers</p>
                  <p className="text-2xl font-bold text-secondary-900">{stats.totalTeachers}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-soft">
              <div className="flex items-center">
                <div className="p-2 bg-success-100 rounded-lg">
                  <svg className="h-6 w-6 text-success-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Active Classes</p>
                  <p className="text-2xl font-bold text-secondary-900">{stats.totalClasses}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-soft">
              <div className="flex items-center">
                <div className="p-2 bg-warning-100 rounded-lg">
                  <svg className="h-6 w-6 text-warning-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Avg Grade</p>
                  <p className="text-2xl font-bold text-secondary-900">{stats.averageGrade}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Today's Attendance */}
          <div className="bg-white rounded-lg shadow-soft p-6">
            <h3 className="text-lg font-medium text-secondary-900 mb-4">Today's Attendance</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{attendanceStats.present}</div>
                <div className="text-sm text-secondary-600">Present</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{attendanceStats.absent}</div>
                <div className="text-sm text-secondary-600">Absent</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">{attendanceStats.late}</div>
                <div className="text-sm text-secondary-600">Late</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">{attendanceStats.percentage}%</div>
                <div className="text-sm text-secondary-600">Attendance Rate</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Academic Performance Report */}
      {selectedReport === 'academic' && (
        <div className="space-y-6">
          {/* Grade Distribution */}
          <div className="bg-white rounded-lg shadow-soft p-6">
            <h3 className="text-lg font-medium text-secondary-900 mb-4">Grade Distribution</h3>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {Object.entries(gradeDistribution).map(([grade, count]) => (
                <div key={grade} className="text-center">
                  <div className={`text-2xl font-bold ${
                    grade === 'A' ? 'text-green-600' :
                    grade === 'B' ? 'text-blue-600' :
                    grade === 'C' ? 'text-yellow-600' :
                    grade === 'D' ? 'text-orange-600' :
                    'text-red-600'
                  }`}>
                    {count}
                  </div>
                  <div className="text-sm text-secondary-600">Grade {grade}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Performers */}
          <div className="bg-white rounded-lg shadow-soft p-6">
            <h3 className="text-lg font-medium text-secondary-900 mb-4">Top 10 Performers</h3>
            <div className="space-y-2">
              {topPerformers.map((student, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-secondary-50 rounded-lg">
                  <div className="flex items-center">
                    <span className="text-lg font-bold text-primary-600 mr-3">#{index + 1}</span>
                    <span className="font-medium text-secondary-900">{student.name}</span>
                  </div>
                  <span className="text-lg font-bold text-success-600">{student.average}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Attendance Report */}
      {selectedReport === 'attendance' && (
        <div className="space-y-6">
          {/* Attendance Trend */}
          <div className="bg-white rounded-lg shadow-soft p-6">
            <h3 className="text-lg font-medium text-secondary-900 mb-4">7-Day Attendance Trend</h3>
            <div className="flex items-end justify-between h-32">
              {attendanceTrend.map((day, index) => (
                <div key={index} className="flex flex-col items-center">
                  <div 
                    className="bg-primary-600 rounded-t w-8 mb-2"
                    style={{ height: `${day.percentage}%` }}
                  ></div>
                  <span className="text-xs text-secondary-600">{day.date}</span>
                  <span className="text-xs font-medium text-secondary-900">{day.percentage}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Attendance Summary */}
          <div className="bg-white rounded-lg shadow-soft p-6">
            <h3 className="text-lg font-medium text-secondary-900 mb-4">Attendance Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{attendanceStats.present}</div>
                <div className="text-sm text-green-700">Present Today</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{attendanceStats.absent}</div>
                <div className="text-sm text-red-700">Absent Today</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{attendanceStats.percentage}%</div>
                <div className="text-sm text-blue-700">Overall Rate</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enrollment Report */}
      {selectedReport === 'enrollment' && (
        <div className="space-y-6">
          {/* Class Enrollment */}
          <div className="bg-white rounded-lg shadow-soft p-6">
            <h3 className="text-lg font-medium text-secondary-900 mb-4">Class Enrollment</h3>
            <div className="space-y-3">
              {Object.entries(classEnrollment).map(([className, count]) => (
                <div key={className} className="flex justify-between items-center p-3 bg-secondary-50 rounded-lg">
                  <span className="font-medium text-secondary-900">{className}</span>
                  <span className="text-lg font-bold text-primary-600">{count} students</span>
                </div>
              ))}
            </div>
          </div>

          {/* Student Status */}
          <div className="bg-white rounded-lg shadow-soft p-6">
            <h3 className="text-lg font-medium text-secondary-900 mb-4">Student Status Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{stats.activeStudents}</div>
                <div className="text-sm text-green-700">Active Students</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-600">{stats.totalStudents - stats.activeStudents}</div>
                <div className="text-sm text-gray-700">Inactive Students</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports; 