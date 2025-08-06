/**
 * Enhanced API Service Layer
 * Centralized API management for Arusha Catholic Seminary Frontend
 */

import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage (auth store)
    const authStorage = localStorage.getItem('auth-storage');
    let token = null;
    
    if (authStorage) {
      try {
        const parsed = JSON.parse(authStorage);
        token = parsed.state?.token;
      } catch (error) {
        console.error('Error parsing auth storage:', error);
      }
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth storage on unauthorized
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Enhanced API wrapper with success/failure handling
const createApiWrapper = (apiCall) => {
  return async (...args) => {
    try {
      const result = await apiCall(...args);
      return {
        success: true,
        data: result,
        message: 'Operation completed successfully'
      };
    } catch (error) {
      const errorMessage = handleApiError(error);
      return {
        success: false,
        error: errorMessage,
        data: null
      };
    }
  };
};

// Error handling utility
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    if (data?.error?.message) {
      return data.error.message;
    }
    
    switch (status) {
      case 400:
        return 'Bad request - please check your input';
      case 401:
        return 'Authentication required - please log in';
      case 403:
        return 'Access denied - insufficient permissions';
      case 404:
        return 'Resource not found';
      case 422:
        return 'Validation error - please check your input';
      case 429:
        return 'Too many requests - please try again later';
      case 500:
        return 'Server error - please try again later';
      default:
        return `Request failed with status ${status}`;
    }
  } else if (error.request) {
    // Network error
    return 'Network error - please check your connection';
  } else {
    // Other error
    return error.message || 'An unexpected error occurred';
  }
};

// Authentication API with enhanced error handling
export const authAPI = {
  login: createApiWrapper((username, password) => 
    api.post('/auth/login', { username, password })
  ),
  
  register: createApiWrapper((userData) => 
    api.post('/auth/register', userData)
  ),
  
  forgotPassword: createApiWrapper((email) => 
    api.post('/auth/forgot-password', { email })
  ),
  
  resetPassword: createApiWrapper((token, newPassword) => 
    api.post('/auth/reset-password', { token, new_password: newPassword })
  ),
  
  refresh: createApiWrapper((refreshToken) => 
    api.post('/auth/refresh', { refresh_token: refreshToken })
  ),
  
  logout: createApiWrapper(() => 
    api.post('/auth/logout')
  ),
  
  getCurrentUser: createApiWrapper(() => 
    api.get('/auth/me')
  ),
  
  updateProfile: createApiWrapper((profileData) => 
    api.put('/auth/profile', profileData)
  ),
  
  changePassword: createApiWrapper((passwordData) => 
    api.put('/auth/change-password', passwordData)
  ),
};

// User Management API with enhanced error handling
export const userAPI = {
  getUsers: createApiWrapper((params = {}) => 
    api.get('/users', { params })
  ),
  
  getUser: createApiWrapper((userId) => 
    api.get(`/users/${userId}`)
  ),
  
  updateUser: createApiWrapper((userId, userData) => 
    api.put(`/users/${userId}`, userData)
  ),
  
  deleteUser: createApiWrapper((userId) => 
    api.delete(`/users/${userId}`)
  ),
};

// Student Management API with enhanced error handling
export const studentAPI = {
  createStudent: createApiWrapper((studentData) => 
    api.post('/students', studentData)
  ),
  
  getStudents: createApiWrapper((params = {}) => 
    api.get('/students', { params })
  ),
  
  getStudent: createApiWrapper((studentId) => 
    api.get(`/students/${studentId}`)
  ),
  
  updateStudent: createApiWrapper((studentId, studentData) => 
    api.put(`/students/${studentId}`, studentData)
  ),
  
  deleteStudent: createApiWrapper((studentId) => 
    api.delete(`/students/${studentId}`)
  ),
  
  getStudentGrades: createApiWrapper((studentId) => 
    api.get(`/students/${studentId}/grades`)
  ),
  
  getStudentAttendance: createApiWrapper((studentId, params = {}) => 
    api.get(`/students/${studentId}/attendance`, { params })
  ),
};

// Teacher Management API with enhanced error handling
export const teacherAPI = {
  createTeacher: createApiWrapper((teacherData) => 
    api.post('/teachers', teacherData)
  ),
  
  getTeachers: createApiWrapper((params = {}) => 
    api.get('/teachers', { params })
  ),
  
  getTeacher: createApiWrapper((teacherId) => 
    api.get(`/teachers/${teacherId}`)
  ),
  
  updateTeacher: createApiWrapper((teacherId, teacherData) => 
    api.put(`/teachers/${teacherId}`, teacherData)
  ),
  
  deleteTeacher: createApiWrapper((teacherId) => 
    api.delete(`/teachers/${teacherId}`)
  ),
  
  getTeacherClasses: createApiWrapper((teacherId) => 
    api.get(`/teachers/${teacherId}/classes`)
  ),
};

// Class Management API with enhanced error handling
export const classAPI = {
  createClass: createApiWrapper((classData) => 
    api.post('/classes', classData)
  ),
  
  getClasses: createApiWrapper((params = {}) => 
    api.get('/classes', { params })
  ),
  
  getClass: createApiWrapper((classId) => 
    api.get(`/classes/${classId}`)
  ),
  
  updateClass: createApiWrapper((classId, classData) => 
    api.put(`/classes/${classId}`, classData)
  ),
  
  deleteClass: createApiWrapper((classId) => 
    api.delete(`/classes/${classId}`)
  ),
  
  getClassStudents: createApiWrapper((classId) => 
    api.get(`/classes/${classId}/students`)
  ),
  
  getClassSubjects: createApiWrapper((classId) => 
    api.get(`/classes/${classId}/subjects`)
  ),
};

// Subject Management API with enhanced error handling
export const subjectAPI = {
  createSubject: createApiWrapper((subjectData) => 
    api.post('/subjects', subjectData)
  ),
  
  getSubjects: createApiWrapper((params = {}) => 
    api.get('/subjects', { params })
  ),
  
  getSubject: createApiWrapper((subjectId) => 
    api.get(`/subjects/${subjectId}`)
  ),
  
  updateSubject: createApiWrapper((subjectId, subjectData) => 
    api.put(`/subjects/${subjectId}`, subjectData)
  ),
  
  deleteSubject: createApiWrapper((subjectId) => 
    api.delete(`/subjects/${subjectId}`)
  ),
};

// Grade Management API with enhanced error handling
export const gradeAPI = {
  createGrade: createApiWrapper((gradeData) => 
    api.post('/grades', gradeData)
  ),
  
  getGrades: createApiWrapper((params = {}) => 
    api.get('/grades', { params })
  ),
  
  getGrade: createApiWrapper((gradeId) => 
    api.get(`/grades/${gradeId}`)
  ),
  
  updateGrade: createApiWrapper((gradeId, gradeData) => 
    api.put(`/grades/${gradeId}`, gradeData)
  ),
  
  deleteGrade: createApiWrapper((gradeId) => 
    api.delete(`/grades/${gradeId}`)
  ),
  
  getStudentGrades: createApiWrapper((studentId, params = {}) => 
    api.get(`/grades/student/${studentId}`, { params })
  ),
  
  getClassGrades: createApiWrapper((classId, params = {}) => 
    api.get(`/grades/class/${classId}`, { params })
  ),
};

// Attendance Management API with enhanced error handling
export const attendanceAPI = {
  createAttendance: createApiWrapper((attendanceData) => 
    api.post('/attendance', attendanceData)
  ),
  
  getAttendance: createApiWrapper((params = {}) => 
    api.get('/attendance', { params })
  ),
  
  getAttendanceRecord: createApiWrapper((attendanceId) => 
    api.get(`/attendance/${attendanceId}`)
  ),
  
  updateAttendance: createApiWrapper((attendanceId, attendanceData) => 
    api.put(`/attendance/${attendanceId}`, attendanceData)
  ),
  
  deleteAttendance: createApiWrapper((attendanceId) => 
    api.delete(`/attendance/${attendanceId}`)
  ),
  
  getStudentAttendance: createApiWrapper((studentId, params = {}) => 
    api.get(`/attendance/student/${studentId}`, { params })
  ),
  
  getClassAttendance: createApiWrapper((classId, params = {}) => 
    api.get(`/attendance/class/${classId}`, { params })
  ),
  
  bulkCreateAttendance: createApiWrapper((attendanceData) => 
    api.post('/attendance/bulk', attendanceData)
  ),
};

// Report Management API with enhanced error handling
export const reportAPI = {
  generateReport: createApiWrapper((reportData) => 
    api.post('/reports/generate', reportData)
  ),
  
  getReports: createApiWrapper((params = {}) => 
    api.get('/reports', { params })
  ),
  
  getReport: createApiWrapper((reportId) => 
    api.get(`/reports/${reportId}`)
  ),
  
  downloadReport: createApiWrapper((reportId, format = 'pdf') => 
    api.get(`/reports/${reportId}/download`, { 
      params: { format },
      responseType: 'blob'
    })
  ),
  
  deleteReport: createApiWrapper((reportId) => 
    api.delete(`/reports/${reportId}`)
  ),
};

// File Management API with enhanced error handling
export const fileAPI = {
  uploadFile: createApiWrapper((file, type = 'general') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    
    return api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }),
  
  getFiles: createApiWrapper((params = {}) => 
    api.get('/files', { params })
  ),
  
  getFile: createApiWrapper((fileId) => 
    api.get(`/files/${fileId}`)
  ),
  
  downloadFile: createApiWrapper((fileId) => 
    api.get(`/files/${fileId}/download`, { responseType: 'blob' })
  ),
  
  deleteFile: createApiWrapper((fileId) => 
    api.delete(`/files/${fileId}`)
  ),
};

// Email Management API with enhanced error handling
export const emailAPI = {
  sendEmail: createApiWrapper((emailData) => 
    api.post('/email/send', emailData)
  ),
  
  getEmailTemplates: createApiWrapper(() => 
    api.get('/email/templates')
  ),
  
  getEmailLogs: createApiWrapper((params = {}) => 
    api.get('/email/logs', { params })
  ),
  
  getEmailLog: createApiWrapper((logId) => 
    api.get(`/email/logs/${logId}`)
  ),
};

// Calendar Management API with enhanced error handling
export const calendarAPI = {
  createEvent: createApiWrapper((eventData) => 
    api.post('/calendar/events', eventData)
  ),
  
  getEvents: createApiWrapper((params = {}) => 
    api.get('/calendar/events', { params })
  ),
  
  getEvent: createApiWrapper((eventId) => 
    api.get(`/calendar/events/${eventId}`)
  ),
  
  updateEvent: createApiWrapper((eventId, eventData) => 
    api.put(`/calendar/events/${eventId}`, eventData)
  ),
  
  deleteEvent: createApiWrapper((eventId) => 
    api.delete(`/calendar/events/${eventId}`)
  ),
  
  getEventCategories: createApiWrapper(() => 
    api.get('/calendar/categories')
  ),
};

// Search Management API with enhanced error handling
export const searchAPI = {
  search: createApiWrapper((query, params = {}) => 
    api.get('/search', { params: { q: query, ...params } })
  ),
  
  searchStudents: createApiWrapper((query, params = {}) => 
    api.get('/search/students', { params: { q: query, ...params } })
  ),
  
  searchTeachers: createApiWrapper((query, params = {}) => 
    api.get('/search/teachers', { params: { q: query, ...params } })
  ),
  
  searchClasses: createApiWrapper((query, params = {}) => 
    api.get('/search/classes', { params: { q: query, ...params } })
  ),
};

// Data Export API with enhanced error handling
export const exportAPI = {
  exportData: createApiWrapper((exportData) => 
    api.post('/export', exportData)
  ),
  
  getExportJobs: createApiWrapper((params = {}) => 
    api.get('/export/jobs', { params })
  ),
  
  getExportJob: createApiWrapper((jobId) => 
    api.get(`/export/jobs/${jobId}`)
  ),
  
  downloadExport: createApiWrapper((jobId) => 
    api.get(`/export/jobs/${jobId}/download`, { responseType: 'blob' })
  ),
  
  cancelExport: createApiWrapper((jobId) => 
    api.post(`/export/jobs/${jobId}/cancel`)
  ),
};

// Monitoring API with enhanced error handling
export const monitoringAPI = {
  getHealth: createApiWrapper(() => 
    api.get('/monitoring/health')
  ),
  
  getMetrics: createApiWrapper((params = {}) => 
    api.get('/monitoring/metrics', { params })
  ),
  
  getAlerts: createApiWrapper((params = {}) => 
    api.get('/monitoring/alerts', { params })
  ),
  
  acknowledgeAlert: createApiWrapper((alertId) => 
    api.post(`/monitoring/alerts/${alertId}/acknowledge`)
  ),
};

// Utility functions
export const apiUtils = {
  // Check if response is successful
  isSuccess: (response) => response && response.success === true,
  
  // Extract data from response
  getData: (response) => response?.data || null,
  
  // Extract error from response
  getError: (response) => response?.error || 'Unknown error occurred',
  
  // Extract message from response
  getMessage: (response) => response?.message || '',
  
  // Create pagination parameters
  createPaginationParams: (page = 1, size = 20, sortBy = null, sortOrder = 'asc') => {
    const params = { page, size };
    if (sortBy) {
      params.sort_by = sortBy;
      params.sort_order = sortOrder;
    }
    return params;
  },
  
  // Create filter parameters
  createFilterParams: (filters = {}) => {
    return Object.entries(filters)
      .filter(([_, value]) => value !== null && value !== undefined && value !== '')
      .reduce((acc, [key, value]) => {
        acc[key] = value;
        return acc;
      }, {});
  },
  
  // Handle file upload with progress
  uploadFileWithProgress: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
  },
};

// Export all APIs
export default {
  auth: authAPI,
  users: userAPI,
  students: studentAPI,
  teachers: teacherAPI,
  classes: classAPI,
  subjects: subjectAPI,
  grades: gradeAPI,
  attendance: attendanceAPI,
  reports: reportAPI,
  files: fileAPI,
  email: emailAPI,
  calendar: calendarAPI,
  search: searchAPI,
  export: exportAPI,
  monitoring: monitoringAPI,
  utils: apiUtils,
}; 