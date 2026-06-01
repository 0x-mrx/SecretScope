import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { findingService } from '../../services/api';
import { 
  ShieldAlert, 
  LayoutDashboard, 
  FolderGit2, 
  Globe, 
  Bug, 
  FileText, 
  Settings as SettingsIcon, 
  LogOut, 
  Download,
  Terminal
} from 'lucide-react';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { email, role, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleExport = async (format: 'json' | 'csv') => {
    try {
      const blob = await findingService.exportAudit(format);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `secretscope_audit_export.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("Failed to export audit log");
    }
  };

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Projects', path: '/projects', icon: FolderGit2 },
    { name: 'Assets', path: '/assets', icon: Globe },
    { name: 'Findings', path: '/findings', icon: Bug },
    { name: 'Reports', path: '/reports', icon: FileText },
    { name: 'Settings', path: '/settings', icon: SettingsIcon },
  ];

  return (
    <div className="flex h-screen bg-cyber-bg text-cyber-text overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-cyber-card border-r border-cyber-border flex flex-col justify-between shrink-0">
        <div>
          {/* Logo */}
          <div className="p-6 border-b border-cyber-border flex items-center gap-3">
            <div className="bg-red-500/10 p-2 rounded-lg border border-red-500/20">
              <ShieldAlert className="w-6 h-6 text-red-500 animate-pulse" />
            </div>
            <div>
              <h1 className="font-bold text-lg leading-none tracking-tight text-white">SecretScope</h1>
              <span className="text-xs text-cyber-muted tracking-widest uppercase font-mono">DevSecOps</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="p-4 space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive 
                      ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20' 
                      : 'text-cyber-muted hover:text-white hover:bg-gray-800/40 border border-transparent'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User profile & actions */}
        <div className="p-4 border-t border-cyber-border bg-gray-950/40 space-y-3">
          <div className="flex items-center gap-3 px-2">
            <div className="bg-indigo-600/10 p-2 rounded-full border border-indigo-500/20 text-indigo-400 font-bold w-9 h-9 flex items-center justify-center text-sm">
              {email ? email[0].toUpperCase() : 'U'}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold truncate text-white">{email}</p>
              <span className="inline-block text-[10px] bg-indigo-500/10 text-indigo-400 font-mono px-2 py-0.5 rounded border border-indigo-500/20">
                {role}
              </span>
            </div>
          </div>

          {/* Audit Export Trigger */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              onClick={() => handleExport('csv')}
              className="flex items-center justify-center gap-1.5 py-2 rounded-md bg-gray-900 border border-cyber-border hover:bg-gray-800 text-cyber-muted hover:text-white transition"
            >
              <Download className="w-3.5 h-3.5" /> CSV
            </button>
            <button
              onClick={() => handleExport('json')}
              className="flex items-center justify-center gap-1.5 py-2 rounded-md bg-gray-900 border border-cyber-border hover:bg-gray-800 text-cyber-muted hover:text-white transition"
            >
              <Download className="w-3.5 h-3.5" /> JSON
            </button>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium text-red-400 hover:text-red-300 hover:bg-red-500/5 transition border border-transparent hover:border-red-500/10"
          >
            <LogOut className="w-5 h-5" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden bg-cyber-bg">
        {/* Header */}
        <header className="h-16 border-b border-cyber-border bg-cyber-card flex items-center justify-between px-8">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-indigo-400" />
            <span className="text-sm font-mono text-indigo-400">~/secretscope/console</span>
          </div>
          <div className="text-xs text-cyber-muted">
            Platform Status: <span className="text-green-500 font-mono font-bold">ONLINE</span>
          </div>
        </header>

        {/* Content body */}
        <div className="flex-1 overflow-y-auto p-8">
          {children}
        </div>
      </main>
    </div>
  );
};
