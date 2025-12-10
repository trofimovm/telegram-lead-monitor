'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '../api/auth';
import { UserResponse, LoginRequest, RegisterRequest } from '../api/types';
import { AxiosError } from 'axios';

interface AuthContextType {
  user: UserResponse | null;
  loading: boolean;
  error: string | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Load user on mount
  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      setLoading(true);
      const userData = await authApi.getCurrentUser();
      setUser(userData);
      setError(null);
    } catch (err) {
      // If token is invalid or expired, clear tokens
      authApi.logout();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (data: LoginRequest) => {
    try {
      setLoading(true);
      setError(null);

      await authApi.login(data);
      const userData = await authApi.getCurrentUser();
      setUser(userData);
    } catch (err) {
      const error = err as AxiosError<{ detail: string }>;
      setError(error.response?.data?.detail || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: RegisterRequest) => {
    try {
      setLoading(true);
      setError(null);

      await authApi.register(data);
      // Don't auto-login after registration, user needs to verify email
    } catch (err) {
      const error = err as AxiosError<{ detail: string }>;
      setError(error.response?.data?.detail || 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
    setError(null);
  };

  const refreshUser = async () => {
    try {
      const userData = await authApi.getCurrentUser();
      setUser(userData);
      setError(null);
    } catch (err) {
      const error = err as AxiosError<{ detail: string }>;
      setError(error.response?.data?.detail || 'Failed to refresh user');
    }
  };

  const clearError = () => {
    setError(null);
  };

  const value: AuthContextType = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    refreshUser,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
