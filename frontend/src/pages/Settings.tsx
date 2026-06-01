import React, { useState, useEffect } from 'react';
import { ShieldCheck, HardDrive, Cpu, Terminal, KeyRound } from 'lucide-react';

export const Settings: React.FC = () => {
  const [provider, setProvider] = useState('local');
  const [envName, setEnvName] = useState('Production');

  useEffect(() => {
    // Simple state indicators
    const storageEnv = import.meta.env.VITE_STORAGE_PROVIDER || 'local';
    setProvider(storageEnv);
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">System Configuration Settings</h2>
        <p className="text-sm text-cyber-muted font-mono">Monitor platform parameters, storage providers, cryptographic flags, and scanning policies</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Storage configuration */}
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-cyber-muted font-mono flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-indigo-400" />
            Storage Backend
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">Active Storage Manager</span>
              <span className="font-mono text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded font-bold uppercase">
                {provider}
              </span>
            </div>
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">Report Retention Path</span>
              <span className="font-mono text-xs text-white">/var/lib/secretscope/storage</span>
            </div>
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">MinIO SSL Security</span>
              <span className="text-red-500 font-bold">FALSE (Local HTTP connection)</span>
            </div>
          </div>
        </div>

        {/* Security configuration */}
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-cyber-muted font-mono flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Security & Encryption
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">Encryption at Rest</span>
              <span className="font-mono text-xs text-emerald-400 font-bold uppercase">AES-256 (Fernet Enabled)</span>
            </div>
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">JWT Auth Session Timeout</span>
              <span className="font-mono text-xs text-white">10080 Minutes (7 Days)</span>
            </div>
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">Rate Limiting API Layer</span>
              <span className="font-mono text-xs text-emerald-400 font-bold uppercase">ENABLED</span>
            </div>
          </div>
        </div>

        {/* Scan architecture info */}
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-cyber-muted font-mono flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-400" />
            Engine Modules & Tasks
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">Celery Beat Scheduler</span>
              <span className="text-emerald-500 font-bold font-mono">ONLINE</span>
            </div>
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">Celery Worker Pool</span>
              <span className="text-emerald-500 font-bold font-mono">CONNECTED</span>
            </div>
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">Active Regex Scan Plugins</span>
              <span className="font-mono text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded font-bold">5 Default + DB custom rules</span>
            </div>
          </div>
        </div>

        {/* Platform environment info */}
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-cyber-muted font-mono flex items-center gap-2">
            <Terminal className="w-4 h-4 text-orange-400" />
            Infrastructure Logs
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">Running Context</span>
              <span className="font-mono text-xs text-white">Docker Compose Containerization</span>
            </div>
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">Database Engine version</span>
              <span className="font-mono text-xs text-white">PostgreSQL 16 Alpine</span>
            </div>
            <div className="flex justify-between items-center bg-gray-950 p-3 rounded-xl border border-cyber-border">
              <span className="text-cyber-muted">FastAPI framework version</span>
              <span className="font-mono text-xs text-white">v0.111.0</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
