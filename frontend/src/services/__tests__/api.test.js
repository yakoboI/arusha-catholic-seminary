import axios from 'axios';
import { authAPI, studentsAPI, teachersAPI, classesAPI, gradesAPI, handleApiError } from '../api';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('Auth API', () => {
    test('login should make POST request to /auth/login', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock-token',
          user: { id: 1, username: 'testuser' }
        }
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await authAPI.login('testuser', 'password123');

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/auth/login', {
        username: 'testuser',
        password: 'password123'
      });
      expect(result).toEqual(mockResponse.data);
    });

    test('register should make POST request to /auth/register', async () => {
      const mockResponse = {
        data: {
          id: 1,
          username: 'newuser',
          email: 'new@example.com'
        }
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123',
        full_name: 'New User'
      };

      const result = await authAPI.register(userData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/auth/register', userData);
      expect(result).toEqual(mockResponse.data);
    });

    test('getCurrentUser should make GET request to /auth/me', async () => {
      const mockResponse = {
        data: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com'
        }
      };
      mockedAxios.get.mockResolvedValue(mockResponse);

      // Set token in localStorage
      localStorage.setItem('token', 'mock-token');

      const result = await authAPI.getCurrentUser();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/auth/me');
      expect(result).toEqual(mockResponse.data);
    });

    test('logout should clear token from localStorage', () => {
      localStorage.setItem('token', 'mock-token');
      
      authAPI.logout();

      expect(localStorage.getItem('token')).toBeNull();
    });
  });

  describe('Students API', () => {
    test('getStudents should make GET request to /students', async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          page: 1,
          size: 10
        }
      };
      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await studentsAPI.getStudents();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/students/');
      expect(result).toEqual(mockResponse.data);
    });

    test('getStudent should make GET request to /students/:id', async () => {
      const mockResponse = {
        data: {
          id: 1,
          admission_number: 'STU001',
          full_name: 'Test Student'
        }
      };
      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await studentsAPI.getStudent(1);

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/students/1');
      expect(result).toEqual(mockResponse.data);
    });

    test('createStudent should make POST request to /students', async () => {
      const mockResponse = {
        data: {
          id: 1,
          admission_number: 'STU001',
          full_name: 'New Student'
        }
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const studentData = {
        admission_number: 'STU001',
        full_name: 'New Student',
        email: 'student@example.com'
      };

      const result = await studentsAPI.createStudent(studentData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/students/', studentData);
      expect(result).toEqual(mockResponse.data);
    });

    test('updateStudent should make PUT request to /students/:id', async () => {
      const mockResponse = {
        data: {
          id: 1,
          full_name: 'Updated Student'
        }
      };
      mockedAxios.put.mockResolvedValue(mockResponse);

      const updateData = {
        full_name: 'Updated Student'
      };

      const result = await studentsAPI.updateStudent(1, updateData);

      expect(mockedAxios.put).toHaveBeenCalledWith('/api/v1/students/1', updateData);
      expect(result).toEqual(mockResponse.data);
    });

    test('deleteStudent should make DELETE request to /students/:id', async () => {
      mockedAxios.delete.mockResolvedValue({ status: 204 });

      await studentsAPI.deleteStudent(1);

      expect(mockedAxios.delete).toHaveBeenCalledWith('/api/v1/students/1');
    });

    test('searchStudents should make GET request with query parameters', async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0
        }
      };
      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await studentsAPI.searchStudents('test');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/students/search?q=test');
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('Teachers API', () => {
    test('getTeachers should make GET request to /teachers', async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          page: 1,
          size: 10
        }
      };
      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await teachersAPI.getTeachers();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/teachers/');
      expect(result).toEqual(mockResponse.data);
    });

    test('createTeacher should make POST request to /teachers', async () => {
      const mockResponse = {
        data: {
          id: 1,
          employee_id: 'TCH001',
          full_name: 'New Teacher'
        }
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const teacherData = {
        employee_id: 'TCH001',
        full_name: 'New Teacher',
        email: 'teacher@example.com'
      };

      const result = await teachersAPI.createTeacher(teacherData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/teachers/', teacherData);
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('Classes API', () => {
    test('getClasses should make GET request to /classes', async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          page: 1,
          size: 10
        }
      };
      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await classesAPI.getClasses();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/classes/');
      expect(result).toEqual(mockResponse.data);
    });

    test('createClass should make POST request to /classes', async () => {
      const mockResponse = {
        data: {
          id: 1,
          name: 'Form 1A',
          level: 'o_level'
        }
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const classData = {
        name: 'Form 1A',
        level: 'o_level',
        capacity: 30
      };

      const result = await classesAPI.createClass(classData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/classes/', classData);
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('Grades API', () => {
    test('getGrades should make GET request to /grades', async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          page: 1,
          size: 10
        }
      };
      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await gradesAPI.getGrades();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/grades/');
      expect(result).toEqual(mockResponse.data);
    });

    test('createGrade should make POST request to /grades', async () => {
      const mockResponse = {
        data: {
          id: 1,
          student_id: 1,
          subject_id: 1,
          test_score: 85
        }
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const gradeData = {
        student_id: 1,
        subject_id: 1,
        test_score: 85,
        exam_score: 90
      };

      const result = await gradesAPI.createGrade(gradeData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/grades/', gradeData);
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('Error Handling', () => {
    test('handleApiError should handle network errors', () => {
      const networkError = {
        message: 'Network Error',
        code: 'NETWORK_ERROR'
      };

      const result = handleApiError(networkError);

      expect(result).toBe('Network error occurred. Please check your connection.');
    });

    test('handleApiError should handle 401 errors', () => {
      const authError = {
        response: {
          status: 401,
          data: { detail: 'Invalid credentials' }
        }
      };

      const result = handleApiError(authError);

      expect(result).toBe('Invalid credentials');
    });

    test('handleApiError should handle 404 errors', () => {
      const notFoundError = {
        response: {
          status: 404,
          data: { detail: 'Resource not found' }
        }
      };

      const result = handleApiError(notFoundError);

      expect(result).toBe('Resource not found');
    });

    test('handleApiError should handle 422 validation errors', () => {
      const validationError = {
        response: {
          status: 422,
          data: {
            detail: [
              { loc: ['body', 'email'], msg: 'Invalid email format' }
            ]
          }
        }
      };

      const result = handleApiError(validationError);

      expect(result).toBe('Invalid email format');
    });

    test('handleApiError should handle 500 server errors', () => {
      const serverError = {
        response: {
          status: 500,
          data: { detail: 'Internal server error' }
        }
      };

      const result = handleApiError(serverError);

      expect(result).toBe('Internal server error');
    });

    test('handleApiError should handle unknown errors', () => {
      const unknownError = {
        message: 'Unknown error'
      };

      const result = handleApiError(unknownError);

      expect(result).toBe('An unexpected error occurred');
    });
  });

  describe('Request Interceptors', () => {
    test('should add authorization header when token exists', async () => {
      localStorage.setItem('token', 'mock-token');
      
      // Mock axios interceptors
      const mockInterceptor = jest.fn();
      mockedAxios.interceptors = {
        request: {
          use: mockInterceptor
        }
      };

      // Trigger a request
      await authAPI.getCurrentUser();

      expect(mockInterceptor).toHaveBeenCalled();
    });

    test('should not add authorization header when token does not exist', async () => {
      // Ensure no token
      localStorage.removeItem('token');
      
      const mockInterceptor = jest.fn();
      mockedAxios.interceptors = {
        request: {
          use: mockInterceptor
        }
      };

      // Trigger a request
      await authAPI.getCurrentUser();

      expect(mockInterceptor).toHaveBeenCalled();
    });
  });
}); 