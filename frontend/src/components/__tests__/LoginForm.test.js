import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginForm from '../LoginForm';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock the API service
jest.mock('../../services/api', () => ({
  authAPI: {
    login: jest.fn(),
  },
  handleApiError: jest.fn(),
}));

const renderLoginForm = () => {
  return render(
    <AuthProvider>
      <LoginForm />
    </AuthProvider>
  );
};

describe('LoginForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form with all required elements', () => {
    renderLoginForm();
    
    expect(screen.getByText(/sign in/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/don't have an account/i)).toBeInTheDocument();
  });

  test('displays validation errors for empty fields', async () => {
    renderLoginForm();
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/username is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  test('displays validation error for short password', async () => {
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, '123');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument();
    });
  });

  test('handles successful login', async () => {
    const mockLoginResponse = {
      access_token: 'mock-token',
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'admin'
      }
    };
    
    const { authAPI } = require('../../services/api');
    authAPI.login.mockResolvedValue(mockLoginResponse);
    
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'password123');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(authAPI.login).toHaveBeenCalledWith('testuser', 'password123');
    });
  });

  test('handles login error', async () => {
    const mockError = new Error('Invalid credentials');
    const { authAPI, handleApiError } = require('../../services/api');
    authAPI.login.mockRejectedValue(mockError);
    handleApiError.mockReturnValue('Invalid credentials');
    
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'wrongpassword');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(authAPI.login).toHaveBeenCalledWith('testuser', 'wrongpassword');
      expect(handleApiError).toHaveBeenCalledWith(mockError);
    });
  });

  test('shows loading state during login', async () => {
    const { authAPI } = require('../../services/api');
    authAPI.login.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'password123');
    fireEvent.click(submitButton);
    
    expect(screen.getByText(/signing in/i)).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  test('toggles password visibility', async () => {
    renderLoginForm();
    
    const passwordInput = screen.getByLabelText(/password/i);
    const toggleButton = screen.getByRole('button', { name: /toggle password visibility/i });
    
    // Password should be hidden by default
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click toggle button
    fireEvent.click(toggleButton);
    
    // Password should be visible
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    // Click toggle button again
    fireEvent.click(toggleButton);
    
    // Password should be hidden again
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('form resets after successful login', async () => {
    const mockLoginResponse = {
      access_token: 'mock-token',
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'admin'
      }
    };
    
    const { authAPI } = require('../../services/api');
    authAPI.login.mockResolvedValue(mockLoginResponse);
    
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'password123');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(authAPI.login).toHaveBeenCalled();
    });
    
    // Form should be reset
    expect(usernameInput).toHaveValue('');
    expect(passwordInput).toHaveValue('');
  });

  test('prevents multiple form submissions', async () => {
    const { authAPI } = require('../../services/api');
    authAPI.login.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'password123');
    
    // Click submit multiple times
    fireEvent.click(submitButton);
    fireEvent.click(submitButton);
    fireEvent.click(submitButton);
    
    // Should only call login once
    await waitFor(() => {
      expect(authAPI.login).toHaveBeenCalledTimes(1);
    });
  });

  test('handles network errors gracefully', async () => {
    const networkError = new Error('Network Error');
    const { authAPI, handleApiError } = require('../../services/api');
    authAPI.login.mockRejectedValue(networkError);
    handleApiError.mockReturnValue('Network error occurred');
    
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'password123');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(handleApiError).toHaveBeenCalledWith(networkError);
    });
  });

  test('validates email format for username field', async () => {
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(usernameInput, 'invalid-email');
    await userEvent.type(passwordInput, 'password123');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
    });
  });

  test('accepts valid email format for username field', async () => {
    const { authAPI } = require('../../services/api');
    authAPI.login.mockResolvedValue({ access_token: 'token', user: {} });
    
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(usernameInput, 'valid@email.com');
    await userEvent.type(passwordInput, 'password123');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(authAPI.login).toHaveBeenCalledWith('valid@email.com', 'password123');
    });
  });
}); 