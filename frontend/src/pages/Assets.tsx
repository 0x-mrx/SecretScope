import React, { useState, useEffect } from 'react';
import { assetService, projectService, scanService } from '../services/api';
import { Asset, Project } from '../types';
import { Plus, Calendar, Play, CheckCircle, RefreshCw, UploadCloud, FileText, Trash2 } from 'lucide-react';

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

  // Batch import state variables
  const [importMode, setImportMode] = useState<'single' | 'batch'>('single');
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const [batchTargets, setBatchTargets] = useState<string[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [batchRegistering, setBatchRegistering] = useState(false);
  const [batchProgress, setBatchProgress] = useState({ current: 0, total: 0 });

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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    processFile(file);
  };

  const processFile = (file: File) => {
    setBatchFile(file);
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      if (text) {
        const lines = text.split(/\r?\n/).map(line => line.trim()).filter(line => line.length > 0);
        setBatchTargets(lines);
      }
    };
    reader.readAsText(file);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;

    try {
      if (importMode === 'single') {
        if (!target.trim()) return;
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
      } else {
        if (batchTargets.length === 0) {
          alert("Please upload a file containing at least one valid target.");
          return;
        }
        setBatchRegistering(true);
        let successCount = 0;
        let failCount = 0;
        for (let i = 0; i < batchTargets.length; i++) {
          setBatchProgress({ current: i + 1, total: batchTargets.length });
          try {
            await assetService.create({
              project_id: Number(projectId),
              type,
              target_url_or_path: batchTargets[i],
              credentials: credentials || undefined,
              schedule_cron: schedule === 'None' ? undefined : schedule
            });
            successCount++;
          } catch (err) {
            console.error(`Failed to register ${batchTargets[i]}:`, err);
            failCount++;
          }
        }
        setBatchRegistering(false);
        setIsModalOpen(false);
        setBatchFile(null);
        setBatchTargets([]);
        setSchedule('None');
        fetchDependencies();
        setMsg(`Batch registration completed! Successfully registered: ${successCount}. Failed: ${failCount}.`);
      }
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
            {loading ? (
              <tr>
                <td colSpan={6} className="text-center font-mono py-12 text-cyber-muted">Loading scan targets...</td>
              </tr>
            ) : assets.length === 0 ? (
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

            {/* Tabs for Single vs Batch */}
            <div className="flex border-b border-cyber-border mb-4">
              <button
                type="button"
                disabled={batchRegistering}
                onClick={() => setImportMode('single')}
                className={`flex-1 pb-2 font-mono text-xs uppercase tracking-wider font-bold border-b-2 transition ${
                  importMode === 'single' ? 'border-indigo-500 text-white' : 'border-transparent text-cyber-muted hover:text-white'
                }`}
              >
                Single Target
              </button>
              <button
                type="button"
                disabled={batchRegistering}
                onClick={() => setImportMode('batch')}
                className={`flex-1 pb-2 font-mono text-xs uppercase tracking-wider font-bold border-b-2 transition ${
                  importMode === 'batch' ? 'border-indigo-500 text-white' : 'border-transparent text-cyber-muted hover:text-white'
                }`}
              >
                Batch Import (.txt)
              </button>
            </div>

            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Scope Project</label>
                <select
                  required
                  disabled={batchRegistering}
                  value={projectId}
                  onChange={(e) => setProjectId(Number(e.target.value))}
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition disabled:opacity-50"
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
                  disabled={batchRegistering}
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition disabled:opacity-50"
                >
                  <option value="WEBSITE">Website (Web Application / HTML / JS / Source Maps)</option>
                  <option value="REPOSITORY">Git Repository (Github / Gitlab URL)</option>
                  <option value="FILE_PATH">Directory Scan (Local Directory Path)</option>
                </select>
              </div>

              {importMode === 'single' ? (
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
              ) : (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Upload Target List (.txt)</label>
                  {batchFile ? (
                    <div className="bg-gray-950 border border-cyber-border rounded-xl p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <FileText className="w-8 h-8 text-indigo-400" />
                        <div>
                          <p className="text-sm font-semibold text-white truncate max-w-[200px]">{batchFile.name}</p>
                          <p className="text-xs text-cyber-muted font-mono">{batchTargets.length} targets loaded</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        disabled={batchRegistering}
                        onClick={() => { setBatchFile(null); setBatchTargets([]); }}
                        className="p-1 hover:bg-gray-800 text-cyber-muted hover:text-rose-400 rounded-lg transition disabled:opacity-50"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  ) : (
                    <div
                      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                      onDragLeave={() => setIsDragOver(false)}
                      onDrop={(e) => {
                        e.preventDefault();
                        setIsDragOver(false);
                        const file = e.dataTransfer.files?.[0];
                        if (file) {
                          processFile(file);
                        }
                      }}
                      className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition ${
                        isDragOver ? 'border-indigo-500 bg-indigo-500/10' : 'border-cyber-border bg-gray-950/40 hover:border-cyber-muted'
                      }`}
                    >
                      <input
                        type="file"
                        accept=".txt"
                        onChange={handleFileChange}
                        className="hidden"
                        id="batch-file-input"
                      />
                      <label htmlFor="batch-file-input" className="cursor-pointer space-y-2 block">
                        <UploadCloud className="w-10 h-10 text-cyber-muted mx-auto" />
                        <div className="text-sm text-white font-semibold">Drag & drop your .txt target file here</div>
                        <div className="text-xs text-cyber-muted">Or click to browse (one target per line)</div>
                      </label>
                    </div>
                  )}
                </div>
              )}

              {type === 'REPOSITORY' && (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Credentials Secret Token (Optional)</label>
                  <input
                    type="password"
                    disabled={batchRegistering}
                    value={credentials}
                    onChange={(e) => setCredentials(e.target.value)}
                    placeholder="OAuth token or SSH passphrase (encrypted at rest)"
                    className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition disabled:opacity-50"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Schedules Frequency</label>
                <select
                  disabled={batchRegistering}
                  value={schedule}
                  onChange={(e) => setSchedule(e.target.value)}
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition disabled:opacity-50"
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
                  disabled={batchRegistering}
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 border border-cyber-border hover:bg-gray-800 text-cyber-text font-semibold py-2.5 rounded-xl text-sm transition disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={batchRegistering || (importMode === 'batch' && batchTargets.length === 0)}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2.5 rounded-xl text-sm transition disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {batchRegistering ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      {batchProgress.current}/{batchProgress.total} Registered
                    </>
                  ) : (
                    importMode === 'single' ? 'Register target' : 'Register targets'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
