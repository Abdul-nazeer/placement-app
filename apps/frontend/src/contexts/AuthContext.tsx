import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { AuthService } from '../services/auth';
import {
  User,
  LoginCredentials,
  RegisterData,
  AuthContextType,
  UserProfile,
} from '../types/auth';

const AuthContext = createContext(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider = ({ children }) => {
  const [isInitialized, setIsInitialized] = useState(false);
  const queryClient = useQueryClient();

  // Query for current user
  const {
    data: user,
    isLoading: isUserLoading,
    error: userError,
  } = useQuery({
    queryKey: ['currentUser'],
    queryFn: AuthService.getCurrentUser,
    enabled: AuthService.isAuthenticated() && isInitialized,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      if (AuthService.isAuthenticated()) {
        try {
          // Verify token is still valid
          const verification = await AuthService.verifyToken();
          if (!verification.valid) {
            // Token is invalid, clear it
            await AuthService.logout();
          }
        } catch (error) {
          // Token verification failed, clear it
          await AuthService.logout();
        }
      }
      setIsInitialized(true);
    };

    initializeAuth();
  }, []);

  // Handle user error (token expired, etc.)
  useEffect(() => {
    if (userError && isInitialized) {
      AuthService.logout();
      queryClient.clear();
    }
  }, [userError, isInitialized, queryClient]);

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      const tokenResponse = await AuthService.login(credentials);
      
      // Update query cache with user data
      queryClient.setQueryData(['currentUser'], tokenResponse.user);
      
      toast.success('Successfully logged in!');
    } catch (error: any) {
      const message = error.response?.data?.message || 'Login failed';
      toast.error(message);
      throw error;
    }
  };

  const register = async (data: RegisterData): Promise<void> => {
    try {
      await AuthService.register(data);
      toast.success('Registration successful! Please log in.');
    } catch (error: any) {
      const message = error.response?.data?.message || 'Registration failed';
      toast.error(message);
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await AuthService.logout();
      queryClient.clear();
      toast.success('Successfully logged out');
    } catch (error) {
      // Continue with logout even if API call fails
      queryClient.clear();
      toast.success('Logged out');
    }
  };

  const refreshToken = async (): Promise<void> => {
    try {
      const tokenResponse = await AuthService.refreshToken();
      queryClient.setQueryData(['currentUser'], tokenResponse.user);
    } catch (error) {
      await logout();
      throw error;
    }
  };

  const updateProfile = async (data: Partial<UserProfile>): Promise<void> => {
    try {
      const updatedProfile = await AuthService.updateUserProfile(data);
      
      // Update user in cache
      queryClient.setQueryData(['currentUser'], (oldUser: User | undefined) => {
        if (oldUser) {
          return {
            ...oldUser,
            profile: updatedProfile,
          };
        }
        return oldUser;
      });

      toast.success('Profile updated successfully!');
    } catch (error: any) {
      const message = error.response?.data?.message || 'Profile update failed';
      toast.error(message);
      throw error;
    }
  };

  const contextValue: AuthContextType = {
    user: user || null,
    isAuthenticated: !!user && AuthService.isAuthenticated(),
    isLoading: !isInitialized || (isInitialized && AuthService.isAuthenticated() && isUserLoading),
    login,
    register,
    logout,
    refreshToken,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};