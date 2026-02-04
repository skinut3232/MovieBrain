import {
  createContext,
  useCallback,
  useContext,
  useState,
  type ReactNode,
} from 'react';
import * as authApi from '../api/auth';

interface AuthContextValue {
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('access_token')
  );

  const saveToken = useCallback((t: string) => {
    localStorage.setItem('access_token', t);
    setToken(t);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    setToken(null);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const resp = await authApi.login(email, password);
      saveToken(resp.access_token);
    },
    [saveToken]
  );

  const register = useCallback(
    async (email: string, password: string) => {
      const resp = await authApi.register(email, password);
      saveToken(resp.access_token);
    },
    [saveToken]
  );

  return (
    <AuthContext.Provider
      value={{ token, isAuthenticated: !!token, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
