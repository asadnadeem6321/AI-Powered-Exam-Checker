import React, { createContext, useState, useContext, useCallback } from 'react';
import { userService } from '../services/examService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const register = useCallback(async (email, name, password, passwordConfirm) => {
    setLoading(true);
    setError(null);
    try {
      const response = await userService.register(email, name, password, passwordConfirm);
      const { user: userData, tokens } = response.data;

      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      setUser(userData);
      setIsAuthenticated(true);

      return userData;
    } catch (err) {
      const errorMessage = err.response?.data?.field_errors || err.response?.data?.error || 'Registration failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await userService.login(email, password);
      const { user: userData, tokens } = response.data;

      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      setUser(userData);
      setIsAuthenticated(true);

      return userData;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setLoading(true);
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      await userService.logout(refreshToken);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      setIsAuthenticated(false);
      setLoading(false);
    }
  }, []);

  const getProfile = useCallback(async () => {
    try {
      const response = await userService.getProfile();
      setUser(response.data.user);
      setIsAuthenticated(true);
      return response.data.user;
    } catch (err) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setIsAuthenticated(false);
      throw err;
    }
  }, []);

  const value = {
    user,
    loading,
    error,
    isAuthenticated,
    register,
    login,
    logout,
    getProfile,
    setError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
