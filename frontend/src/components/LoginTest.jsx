import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/useAuthStore';
import { useFeedback } from '../contexts/FeedbackContext';

const LoginTest = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated, user } = useAuthStore();
  const { showSuccess, showError, showLoading, hideLoading } = useFeedback();
  const [testCredentials] = useState({
    username: 'admin',
    password: 'admin123'
  });

  const handleTestLogin = async () => {
    try {
      showLoading('Testing login...');
      const result = await login(testCredentials.username, testCredentials.password);
      hideLoading();
      
      if (result.success) {
        showSuccess('Test login successful! Redirecting to dashboard...', 'Test Success');
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } else {
        showError(`Test login failed: ${result.error}`, 'Test Failed');
      }
    } catch (error) {
      hideLoading();
      showError('Test login error occurred', 'Test Error');
    }
  };

  const handleDirectNavigation = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-secondary-900">
            Login Flow Test
          </h2>
          <p className="mt-2 text-center text-sm text-secondary-600">
            Test the login to dashboard flow
          </p>
        </div>
        
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Current State</h3>
            <p className="text-sm text-gray-600">
              <strong>Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}
            </p>
            {user && (
              <p className="text-sm text-gray-600">
                <strong>User:</strong> {user.full_name} ({user.role})
              </p>
            )}
          </div>
          
          <button
            onClick={handleTestLogin}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Test Login Flow
          </button>
          
          <button
            onClick={handleDirectNavigation}
            className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Go Directly to Dashboard
          </button>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-blue-900 mb-2">Test Credentials</h4>
            <p className="text-xs text-blue-700">
              Username: {testCredentials.username}<br />
              Password: {testCredentials.password}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginTest; 