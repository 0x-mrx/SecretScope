import React, { useState, useEffect } from 'react';
import { assetService, projectService, scanService } from '../services/api';
import { Asset, Project } from '../types';
import { Shield, Plus, Calendar, Play, CheckCircle, RefreshCw } from 'lucide-react';

export const Assets: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [projectId, setProjectId] = useState<number | ''>('');
  const [type, setType] = useState('WEBSITE'); // WEBSITE, REPOSITORY, FILE_PATH
  const [target, setTarget] = useState('');
  const [credentials, setCredentials] = useState('');
  const [schedule, setSchedule] = useState('None'); // None, hourly, daily, weekly

  const [loading, setLoading] = useState(false);
  const [triggeringIds, setTriggeringIds] = useState<number[]>([]);
  const [msg, setMsg] = useState('');

  const fetchDependencies = async () => {
    setLoading(true);
    try {
      const projData = await projectService.list();
      setProjects(projData);
      
      const assetData = await assetService.list(selectedProject || undefined);
      setAssets(assetData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDependencies();
  }, [selectedProject]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !target.trim()) return;

    try {
      await assetService.create({
        project_id: Number(projectId),
        type,
        target_url_or_path: target,
        credentials: credentials || undefined,
        schedule_cron: schedule === 'None' ? undefined : schedule
      });
      setIsModalOpen(false);
      setTarget('');
      setCredentials('');
      setSchedule('None');
      fetchDependencies();
    } catch (err) {
      alert("Failed to register scanning target asset");
    }
  };

  const triggerScan = async (assetId: number) => {
    setTriggeringIds(prev => [...prev, assetId]);
    setMsg('');
    try {
      await scanService.start(assetId);
      setMsg("Scan successfully queued! Monitor findings or Celery terminal logs.");
    } catch (err) {
      alert("Failed to start scanner task");
    } finally {
      setTriggeringIds(prev => prev.filter(id => id !== assetId));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Active Target Coverage</h2>
          <p className="text-sm text-cyber-muted font-mono">Monitored domains, public/internal git servers, and system environments</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl font-semibold shadow-lg transition"
        >
          <Plus className="w-5 h-5" /> Register Scan Asset
        </button>
      </div>

      {msg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-sm text-emerald-400 flex items-center gap-2">
          <CheckCircle className="w-5 h-5" />
          {msg}
        </div>
      )}

      {/* Filter bar */}
      <div className="bg-cyber-card border border-cyber-border p-4 rounded-2xl flex items-center gap-4">
        <label className="text-sm font-semibold text-cyber-muted font-mono">Scope Filter:</label>
        <select
          value={selectedProject || ''}
          onChange={(e) => setSelectedProject(e.target.value ? Number(e.target.value) : null)}
          className="bg-gray-950 border border-cyber-border text-white text-sm rounded-xl py-2 px-4 outline-none focus:border-indigo-500"
        >
          <option value="">All Projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      {/* Assets Table */}
      <div className="bg-cyber-card border border-cyber-border rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-cyber-border">
          <h3 className="font-bold text-white">Target Inventory</h3>
        </div>
        <table className="w-full text-sm text-left border-collapse">
          <thead>
            <tr className="bg-gray-950/60 text-cyber-muted border-b border-cyber-border font-mono text-xs">
              <th className="p-4">Type</th>
              <th className="p-4">Target Address / Path</th>
              <th className="p-4">Schedule</th>
              <th className="p-4">Status</th>
              <th className="p-4">Last Scanned</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {assets.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center font-mono py-12 text-cyber-muted">No scan targets matching filter scope.</td>
              </tr>
            ) : (
              assets.map((asset) => (
                <tr key={asset.id} className="border-b border-cyber-border hover:bg-gray-900/30 transition">
                  <td className="p-4">
                    <span className="inline-block bg-gray-950 border border-cyber-border text-indigo-400 font-mono text-xs px-2 py-0.5 rounded">
                      {asset.type}
                    </span>
                  </td>
                  <td className="p-4 font-mono text-white text-xs truncate max-w-md">
                    {asset.target_url_or_path}
                  </td>
                  <td className="p-4 text-cyber-muted font-mono text-xs flex items-center gap-1.5 mt-2.5">
                    <Calendar className="w-3.5 h-3.5" />
                    {asset.schedule_cron || 'manual'}
                  </td>
                  <td className="p-4">
                    <span className="text-emerald-500 font-bold font-mono text-xs">ACTIVE</span>
                  </td>
                  <td className="p-4 text-cyber-muted font-mono text-xs">
                    {asset.last_scanned_at ? new Date(asset.last_scanned_at).toLocaleString() : 'Never'}
                  </td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => triggerScan(asset.id)}
                      disabled={triggeringIds.includes(asset.id)}
                      className="inline-flex items-center gap-1.5 bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 hover:text-white px-3 py-1.5 rounded-lg border border-indigo-500/20 text-xs font-semibold transition disabled:opacity-50"
                    >
                      {triggeringIds.includes(asset.id) ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Scanning
                        </>
                      ) : (
                        <>
                          <Play className="w-3.5 h-3.5" /> Scan Target
                        </>
                      )}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Register Asset Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-6 z-50 animate-fade-in">
          <div className="bg-cyber-card border border-cyber-border rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
            <h3 className="text-lg font-bold text-white mb-4">Register Scan Target Asset</h3>

            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Scope Project</label>
                <select
                  required
                  value={projectId}
                  onChange={(e) => setProjectId(Number(e.target.value))}
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition"
                >
                  <option value="">Select Target Project...</option>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Asset Target Type</label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition"
                >
                  <option value="WEBSITE">Website (Web Application / HTML / JS / Source Maps)</option>
                  <option value="REPOSITORY">Git Repository (Github / Gitlab URL)</option>
                  <option value="FILE_PATH">Directory Scan (Local Directory Path)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Target Address / Path</label>
                <input
                  type="text"
                  required
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder={type === 'WEBSITE' ? 'https://example.com' : type === 'REPOSITORY' ? 'https://github.com/org/repo.git' : '/absolute/path/to/project'}
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm font-mono outline-none transition"
                />
              </div>

              {type === 'REPOSITORY' && (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Credentials Secret Token (Optional)</label>
                  <input
                    type="password"
                    value={credentials}
                    onChange={(e) => setCredentials(e.target.value)}
                    placeholder="OAuth token or SSH passphrase (encrypted at rest)"
                    className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Schedules Frequency</label>
                <select
                  value={schedule}
                  onChange={(e) => setSchedule(e.target.value)}
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition"
                >
                  <option value="None">Manual Scan only</option>
                  <option value="hourly">Run scan Hourly</option>
                  <option value="daily">Run scan Daily</option>
                  <option value="weekly">Run scan Weekly</option>
                </select>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 border border-cyber-border hover:bg-gray-800 text-cyber-text font-semibold py-2.5 rounded-xl text-sm transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2.5 rounded-xl text-sm transition"
                >
                  Register target
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
