import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/layout/Layout';

// Pages
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Projects } from './pages/Projects';
import { Assets } from './pages/Assets';
import { Findings } from './pages/Findings';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Layout>{children}</Layout> : <Navigate to="/login" replace />;
};

export const AppContent: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Private Routes */}
        <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/projects" element={<PrivateRoute><Projects /></PrivateRoute>} />
        <Route path="/assets" element={<PrivateRoute><Assets /></PrivateRoute>} />
        <Route path="/findings" element={<PrivateRoute><Findings /></PrivateRoute>} />
        <Route path="/reports" element={<PrivateRoute><Reports /></PrivateRoute>} />
        <Route path="/settings" element={<PrivateRoute><Settings /></PrivateRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
