import { createContext, useContext, useCallback, useEffect, useState, type ReactNode } from 'react';
import { getMe, logout as apiLogout } from '../api/auth.api';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAccessToken: (token: string) => void;
  refreshUser: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  const setAccessToken = useCallback((token: string) => {
    localStorage.setItem('access_token', token);
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setUser(null);
        return;
      }
      const userData = await getMe();
      setUser(userData);
    } catch {
      setUser(null);
      localStorage.removeItem('access_token');
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch {
      // Even if the API call fails, clear local state
    } finally {
      localStorage.removeItem('access_token');
      setUser(null);
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      await refreshUser();
      setIsLoading(false);
    };
    init();
  }, [refreshUser]);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, isLoading, setAccessToken, refreshUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
}
