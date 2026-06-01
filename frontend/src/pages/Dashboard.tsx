import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/api';
import { DashboardData } from '../types';
import { 
  ShieldAlert, 
  Clock, 
  Award, 
  FileWarning, 
  Terminal, 
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchMetrics = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await dashboardService.getMetrics();
      setData(res);
    } catch (err: any) {
      setError("Failed to retrieve dashboard analytics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <RefreshCw className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-sm font-mono text-cyber-muted">Aggregating platform metrics...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-xl text-center">
        <p className="text-red-400 font-semibold">{error || "No dashboard data available"}</p>
        <button onClick={fetchMetrics} className="mt-4 px-4 py-2 bg-red-500/20 rounded-lg hover:bg-red-500/30 text-white font-medium text-sm transition">
          Retry Connection
        </button>
      </div>
    );
  }

  const { severity_distribution, asset_metrics, mttr_hours, sla_compliance_percentage, open_findings_trend, recent_activity } = data;

  const totalFindings = severity_distribution.CRITICAL + severity_distribution.HIGH + severity_distribution.MEDIUM + severity_distribution.LOW;

  // Pie chart format
  const severityData = [
    { name: 'Critical', value: severity_distribution.CRITICAL, color: '#f43f5e' },
    { name: 'High', value: severity_distribution.HIGH, color: '#f97316' },
    { name: 'Medium', value: severity_distribution.MEDIUM, color: '#eab308' },
    { name: 'Low', value: severity_distribution.LOW, color: '#3b82f6' },
  ].filter(item => item.value > 0);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Title */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Executive Compliance Console</h2>
          <p className="text-sm text-cyber-muted font-mono">Platform overview & critical vulnerability indexing</p>
        </div>
        <button
          onClick={fetchMetrics}
          className="flex items-center gap-2 px-4 py-2 bg-gray-900 border border-cyber-border rounded-xl hover:bg-gray-800 text-sm font-semibold transition"
        >
          <RefreshCw className="w-4 h-4" /> Refresh console
        </button>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Total Findings Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 relative overflow-hidden group hover:border-indigo-500/40 transition-all duration-300">
          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-full blur-2xl pointer-events-none"></div>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-cyber-muted font-mono">Total Exposed Secrets</p>
              <h3 className="text-3xl font-bold text-white mt-3">{totalFindings}</h3>
            </div>
            <div className="bg-indigo-500/15 p-3 rounded-xl text-indigo-400 border border-indigo-500/20">
              <ShieldAlert className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex gap-2 text-xs">
            <span className="text-red-400 font-bold">{severity_distribution.CRITICAL} Critical</span>
            <span className="text-orange-400 font-bold">{severity_distribution.HIGH} High</span>
          </div>
        </div>

        {/* SLA Compliance Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 relative overflow-hidden group hover:border-emerald-500/40 transition-all duration-300">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl pointer-events-none"></div>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-cyber-muted font-mono">Remediation SLA Compliance</p>
              <h3 className="text-3xl font-bold text-emerald-400 mt-3">{sla_compliance_percentage}%</h3>
            </div>
            <div className="bg-emerald-500/15 p-3 rounded-xl text-emerald-400 border border-emerald-500/20">
              <Award className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 text-xs text-cyber-muted">
            Resolving exposures within SLA targets
          </div>
        </div>

        {/* MTTR Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 relative overflow-hidden group hover:border-sky-500/40 transition-all duration-300">
          <div className="absolute top-0 right-0 w-24 h-24 bg-sky-500/5 rounded-full blur-2xl pointer-events-none"></div>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-cyber-muted font-mono">Mean Time To Remediate (MTTR)</p>
              <h3 className="text-3xl font-bold text-sky-400 mt-3">{mttr_hours}h</h3>
            </div>
            <div className="bg-sky-500/15 p-3 rounded-xl text-sky-400 border border-sky-500/20">
              <Clock className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 text-xs text-cyber-muted">
            Average hours from discovery to close
          </div>
        </div>

        {/* Asset Coverage Card */}
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 relative overflow-hidden group hover:border-gray-500/40 transition-all duration-300">
          <div className="absolute top-0 right-0 w-24 h-24 bg-gray-500/5 rounded-full blur-2xl pointer-events-none"></div>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-cyber-muted font-mono">Monitored Assets</p>
              <h3 className="text-3xl font-bold text-white mt-3">{asset_metrics.TOTAL}</h3>
            </div>
            <div className="bg-gray-500/15 p-3 rounded-xl text-gray-400 border border-gray-500/20">
              <FileWarning className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex gap-2 text-xs text-cyber-muted font-mono">
            <span>{asset_metrics.WEBSITE} Web</span>
            <span>{asset_metrics.REPOSITORY} Git</span>
          </div>
        </div>
      </div>

      {/* Charts section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend line */}
        <div className="lg:col-span-2 bg-cyber-card border border-cyber-border rounded-2xl p-6">
          <h4 className="text-sm font-semibold uppercase tracking-wider text-cyber-muted font-mono mb-6">Open Findings Trend</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={open_findings_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="date" stroke="#9ca3af" fontSize={11} />
                <YAxis stroke="#9ca3af" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#1f2937', color: '#f3f4f6' }} />
                <Area type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#colorCount)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity distribution */}
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 flex flex-col justify-between">
          <h4 className="text-sm font-semibold uppercase tracking-wider text-cyber-muted font-mono mb-4">Severity Index</h4>
          {severityData.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center">
              <AlertTriangle className="w-8 h-8 text-green-500 mb-2" />
              <p className="text-sm font-mono text-green-400">Zero exposed secrets found</p>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center">
              <div className="w-full h-44">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={severityData}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={65}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {severityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#1f2937' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="w-full space-y-2 mt-4 text-xs font-semibold">
                {severityData.map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center bg-gray-950/40 px-3 py-1.5 rounded-lg border border-cyber-border">
                    <span className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                      {item.name}
                    </span>
                    <span>{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Activity Log / Feed */}
      <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-6">
          <Terminal className="w-5 h-5 text-indigo-400" />
          <h4 className="text-sm font-semibold uppercase tracking-wider text-cyber-muted font-mono">Audit Log Monitor</h4>
        </div>
        <div className="space-y-4">
          {recent_activity.map((act, index) => (
            <div key={index} className="flex justify-between items-start border-b border-cyber-border pb-3 last:border-0 last:pb-0 text-sm">
              <div>
                <span className="inline-block bg-gray-950 border border-cyber-border text-indigo-400 font-mono text-[10px] px-2 py-0.5 rounded mr-3">
                  {act.action}
                </span>
                <span className="text-cyber-text leading-tight">{act.details}</span>
              </div>
              <span className="text-xs text-cyber-muted font-mono shrink-0 ml-4">{act.timestamp}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
