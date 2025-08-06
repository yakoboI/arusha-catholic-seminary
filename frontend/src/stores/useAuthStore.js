import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { authAPI } from '../services/api';

const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (username, password) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authAPI.login(username, password);
          
          if (response.success) {
            const { access_token, refresh_token, user } = response.data;
            
            set({
              user,
              token: access_token,
              refreshToken: refresh_token,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            
            return { success: true, user };
          } else {
            set({
              isLoading: false,
              error: response.error,
              isAuthenticated: false,
            });
            
            return { success: false, error: response.error };
          }
          
        } catch (error) {
          console.error('Login error:', error);
          const errorMessage = 'An unexpected error occurred during login';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
          });
          
          return { success: false, error: errorMessage };
        }
      },

      logout: async () => {
        try {
          // Call logout endpoint
          await authAPI.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          // Clear local state regardless of API call success
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authAPI.register(userData);
          
          if (response.success) {
            // Registration doesn't automatically log in the user
            // They need to login separately
            set({
              isLoading: false,
              error: null,
            });
            
            return { success: true, message: response.data.message };
          } else {
            set({
              isLoading: false,
              error: response.error,
              isAuthenticated: false,
            });
            
            return { success: false, error: response.error };
          }
          
        } catch (error) {
          const errorMessage = 'An unexpected error occurred during registration';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
          });
          
          return { success: false, error: errorMessage };
        }
      },

      updateProfile: async (profileData) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authAPI.updateProfile(profileData);
          
          if (response.success) {
            const updatedUser = response.data;
            
            set({
              user: { ...get().user, ...updatedUser },
              isLoading: false,
              error: null,
            });
            
            return { success: true, user: updatedUser };
          } else {
            set({
              isLoading: false,
              error: response.error,
            });
            
            return { success: false, error: response.error };
          }
          
        } catch (error) {
          const errorMessage = 'An unexpected error occurred while updating profile';
          set({
            isLoading: false,
            error: errorMessage,
          });
          
          return { success: false, error: errorMessage };
        }
      },

      changePassword: async (passwordData) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authAPI.changePassword(passwordData);
          
          if (response.success) {
            set({
              isLoading: false,
              error: null,
            });
            
            return { success: true };
          } else {
            set({
              isLoading: false,
              error: response.error,
            });
            
            return { success: false, error: response.error };
          }
          
        } catch (error) {
          const errorMessage = 'An unexpected error occurred while changing password';
          set({
            isLoading: false,
            error: errorMessage,
          });
          
          return { success: false, error: errorMessage };
        }
      },

      refreshUser: async () => {
        if (!get().token) return;
        
        set({ isLoading: true, error: null });
        
        try {
          const response = await authAPI.getCurrentUser();
          
          if (response.success) {
            const user = response.data;
            
            set({
              user,
              isLoading: false,
              error: null,
            });
            
            return { success: true, user };
          } else {
            // If token is invalid, logout
            if (response.error.includes('Unauthorized')) {
              get().logout();
            }
            
            set({
              isLoading: false,
              error: response.error,
            });
            
            return { success: false, error: response.error };
          }
          
        } catch (error) {
          // If token is invalid, logout
          if (error.response?.status === 401) {
            get().logout();
          }
          
          const errorMessage = 'Failed to refresh user data';
          set({
            isLoading: false,
            error: errorMessage,
          });
          
          return { success: false, error: errorMessage };
        }
      },

      clearError: () => {
        set({ error: null });
      },

      // Computed values
      hasRole: (role) => {
        const { user } = get();
        return user?.role === role;
      },

      hasAnyRole: (roles) => {
        const { user } = get();
        return roles.includes(user?.role);
      },

      canAccess: (requiredRole) => {
        const { user } = get();
        if (!user) return false;
        
        const roleHierarchy = {
          admin: ['admin', 'administrator', 'teacher', 'student', 'parent', 'non_teaching_staff'],
          administrator: ['administrator', 'teacher', 'student', 'parent', 'non_teaching_staff'],
          teacher: ['teacher', 'student'],
          student: ['student'],
          parent: ['parent'],
          non_teaching_staff: ['non_teaching_staff'],
        };
        
        return roleHierarchy[user.role]?.includes(requiredRole) || false;
      },

      // Utility methods
      getToken: () => get().token,
      getUser: () => get().user,
      getIsAuthenticated: () => get().isAuthenticated,
      getIsLoading: () => get().isLoading,
      getError: () => get().error,
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore; 