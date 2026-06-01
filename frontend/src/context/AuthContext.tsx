import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  token: string | null;
  role: string | null;
  email: string | null;
  isAuthenticated: boolean;
  login: (token: string, role: string, email: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [role, setRole] = useState<string | null>(localStorage.getItem('role'));
  const [email, setEmail] = useState<string | null>(localStorage.getItem('email'));

  const login = (token: string, role: string, email: string) => {
    localStorage.setItem('token', token);
    localStorage.setItem('role', role);
    localStorage.setItem('email', email);
    setToken(token);
    setRole(role);
    setEmail(email);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('email');
    setToken(null);
    setRole(null);
    setEmail(null);
  };

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{ token, role, email, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
