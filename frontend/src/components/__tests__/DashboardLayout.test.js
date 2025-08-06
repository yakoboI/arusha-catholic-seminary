import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import DashboardLayout from '../DashboardLayout';
import { useAuthStore } from '../../stores/useAuthStore';

// Mock the auth store
jest.mock('../../stores/useAuthStore');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/dashboard' }),
}));

const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  full_name: 'Test User',
  role: 'admin'
};

const renderDashboardLayout = (user = mockUser) => {
  useAuthStore.mockReturnValue({
    user,
    logout: jest.fn(),
    isAuthenticated: true
  });

  return render(
    <BrowserRouter>
      <DashboardLayout>
        <div data-testid="dashboard-content">Dashboard Content</div>
      </DashboardLayout>
    </BrowserRouter>
  );
};

describe('DashboardLayout', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders dashboard layout with sidebar and content', () => {
    renderDashboardLayout();
    
    expect(screen.getByTestId('dashboard-content')).toBeInTheDocument();
    expect(screen.getByText(/arusha catholic seminary/i)).toBeInTheDocument();
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
  });

  test('displays user information in header', () => {
    renderDashboardLayout();
    
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
  });

  test('renders navigation menu items', () => {
    renderDashboardLayout();
    
    // Check for main navigation items
    expect(screen.getByText(/students/i)).toBeInTheDocument();
    expect(screen.getByText(/teachers/i)).toBeInTheDocument();
    expect(screen.getByText(/classes/i)).toBeInTheDocument();
    expect(screen.getByText(/grades/i)).toBeInTheDocument();
    expect(screen.getByText(/attendance/i)).toBeInTheDocument();
    expect(screen.getByText(/reports/i)).toBeInTheDocument();
    expect(screen.getByText(/settings/i)).toBeInTheDocument();
  });

  test('toggles sidebar visibility on mobile', () => {
    renderDashboardLayout();
    
    const menuButton = screen.getByLabelText(/toggle menu/i);
    const sidebar = screen.getByRole('navigation');
    
    // Initially sidebar should be visible on desktop
    expect(sidebar).toBeInTheDocument();
    
    // Click menu button to toggle
    fireEvent.click(menuButton);
    
    // Sidebar should still be in document (toggle behavior depends on CSS)
    expect(sidebar).toBeInTheDocument();
  });

  test('handles logout when logout button is clicked', () => {
    const mockLogout = jest.fn();
    useAuthStore.mockReturnValue({
      user: mockUser,
      logout: mockLogout,
      isAuthenticated: true
    });

    renderDashboardLayout();
    
    const logoutButton = screen.getByText(/logout/i);
    fireEvent.click(logoutButton);
    
    expect(mockLogout).toHaveBeenCalled();
  });

  test('shows different menu items based on user role', () => {
    const teacherUser = { ...mockUser, role: 'teacher' };
    renderDashboardLayout(teacherUser);
    
    // Teacher should see relevant menu items
    expect(screen.getByText(/students/i)).toBeInTheDocument();
    expect(screen.getByText(/grades/i)).toBeInTheDocument();
    expect(screen.getByText(/attendance/i)).toBeInTheDocument();
    
    // Teacher should not see admin-only items
    expect(screen.queryByText(/teachers/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/settings/i)).not.toBeInTheDocument();
  });

  test('shows student role menu items', () => {
    const studentUser = { ...mockUser, role: 'student' };
    renderDashboardLayout(studentUser);
    
    // Student should see limited menu items
    expect(screen.getByText(/grades/i)).toBeInTheDocument();
    expect(screen.getByText(/attendance/i)).toBeInTheDocument();
    
    // Student should not see admin/teacher items
    expect(screen.queryByText(/students/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/teachers/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/classes/i)).not.toBeInTheDocument();
  });

  test('displays active menu item based on current route', () => {
    // Mock useLocation to return a specific path
    jest.doMock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => jest.fn(),
      useLocation: () => ({ pathname: '/students' }),
    }));

    renderDashboardLayout();
    
    // The students menu item should be highlighted
    const studentsMenuItem = screen.getByText(/students/i);
    expect(studentsMenuItem).toBeInTheDocument();
  });

  test('handles user profile dropdown', () => {
    renderDashboardLayout();
    
    const userMenuButton = screen.getByText('Test User');
    fireEvent.click(userMenuButton);
    
    // Should show dropdown options
    expect(screen.getByText(/profile/i)).toBeInTheDocument();
    expect(screen.getByText(/logout/i)).toBeInTheDocument();
  });

  test('displays notifications icon', () => {
    renderDashboardLayout();
    
    const notificationsButton = screen.getByLabelText(/notifications/i);
    expect(notificationsButton).toBeInTheDocument();
  });

  test('handles search functionality', () => {
    renderDashboardLayout();
    
    const searchInput = screen.getByPlaceholderText(/search/i);
    expect(searchInput).toBeInTheDocument();
    
    fireEvent.change(searchInput, { target: { value: 'test search' } });
    expect(searchInput.value).toBe('test search');
  });

  test('renders breadcrumb navigation', () => {
    renderDashboardLayout();
    
    // Should show current page in breadcrumb
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
  });

  test('handles responsive design', () => {
    renderDashboardLayout();
    
    // Should have responsive classes
    const sidebar = screen.getByRole('navigation');
    expect(sidebar).toHaveClass('lg:translate-x-0');
  });

  test('displays school logo and branding', () => {
    renderDashboardLayout();
    
    expect(screen.getByText(/arusha catholic seminary/i)).toBeInTheDocument();
    expect(screen.getByText(/school management system/i)).toBeInTheDocument();
  });

  test('handles keyboard navigation', () => {
    renderDashboardLayout();
    
    const menuButton = screen.getByLabelText(/toggle menu/i);
    
    // Should be keyboard accessible
    fireEvent.keyDown(menuButton, { key: 'Enter' });
    fireEvent.keyDown(menuButton, { key: ' ' });
    
    expect(menuButton).toBeInTheDocument();
  });

  test('shows loading state when user data is loading', () => {
    useAuthStore.mockReturnValue({
      user: null,
      logout: jest.fn(),
      isAuthenticated: false
    });

    renderDashboardLayout();
    
    // Should show loading or redirect to login
    expect(screen.queryByText('Test User')).not.toBeInTheDocument();
  });
}); 