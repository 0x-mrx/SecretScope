import React, { useState, useEffect } from 'react';
import { reportService, projectService } from '../services/api';
import { Report, Project } from '../types';
import { FileText, Plus, Download, RefreshCw, CheckCircle, FileCode } from 'lucide-react';

export const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | ''>('');

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [projId, setProjId] = useState<number | ''>('');
  const [format, setFormat] = useState<'PDF' | 'HTML' | 'MD'>('PDF');

  const [loading, setLoading] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [msg, setMsg] = useState('');

  const fetchReports = async () => {
    setLoading(true);
    try {
      const data = await reportService.list(selectedProject || undefined);
      setReports(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const data = await projectService.list();
      setProjects(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    fetchReports();
  }, [selectedProject]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projId) return;

    setTriggering(true);
    setMsg('');
    try {
      await reportService.generate(Number(projId), format);
      setIsModalOpen(false);
      setMsg("Report generator task dispatched successfully! Refreshing reports table...");
      // Poll reports
      setTimeout(() => {
        fetchReports();
      }, 2000);
    } catch (err) {
      alert("Failed to queue report generation");
    } finally {
      setTriggering(false);
    }
  };

  const downloadReport = async (reportId: number, filename: string) => {
    try {
      const blob = await reportService.download(reportId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("Failed to download file from storage backend");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Compliance & Executive Reporting</h2>
          <p className="text-sm text-cyber-muted font-mono">Download structured PDF, Markdown, and HTML reports for executive triage</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl font-semibold shadow-lg transition"
        >
          <Plus className="w-5 h-5" /> Generate Audit Report
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
          onChange={(e) => setSelectedProject(e.target.value ? Number(e.target.value) : '')}
          className="bg-gray-950 border border-cyber-border text-white text-sm rounded-xl py-2 px-4 outline-none focus:border-indigo-500"
        >
          <option value="">All Projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      {/* Reports Table */}
      <div className="bg-cyber-card border border-cyber-border rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-cyber-border">
          <h3 className="font-bold text-white">Generated Report Inventory</h3>
        </div>
        <table className="w-full text-sm text-left border-collapse">
          <thead>
            <tr className="bg-gray-950/60 text-cyber-muted border-b border-cyber-border font-mono text-xs">
              <th className="p-4">ID</th>
              <th className="p-4">Report Format</th>
              <th className="p-4">Storage URI / Key</th>
              <th className="p-4">Created Date</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && reports.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center font-mono py-12 text-cyber-muted">Connecting reporting directory...</td>
              </tr>
            ) : reports.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center font-mono py-12 text-cyber-muted">No generated reports matching filter scope.</td>
              </tr>
            ) : (
              reports.map((rep) => {
                const parts = rep.file_path.split("/");
                const filename = parts[parts.length - 1];
                return (
                  <tr key={rep.id} className="border-b border-cyber-border hover:bg-gray-900/30 transition">
                    <td className="p-4 font-mono text-xs text-cyber-muted">#{rep.id}</td>
                    <td className="p-4">
                      <span className="inline-flex items-center gap-1.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-mono text-xs px-2.5 py-1 rounded">
                        <FileCode className="w-3.5 h-3.5" />
                        {rep.type}
                      </span>
                    </td>
                    <td className="p-4 font-mono text-xs text-white truncate max-w-sm">
                      {rep.file_path}
                    </td>
                    <td className="p-4 text-cyber-muted font-mono text-xs">
                      {new Date(rep.created_at).toLocaleString()}
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => downloadReport(rep.id, filename)}
                        className="inline-flex items-center gap-1.5 bg-gray-900 border border-cyber-border hover:bg-gray-800 text-cyber-muted hover:text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition"
                      >
                        <Download className="w-3.5 h-3.5" /> Download Report
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Generate Report Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-6 z-50 animate-fade-in">
          <div className="bg-cyber-card border border-cyber-border rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
            <h3 className="text-lg font-bold text-white mb-4">Generate Compliance Report</h3>

            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Scope Project Boundary</label>
                <select
                  required
                  value={projId}
                  onChange={(e) => setProjId(Number(e.target.value))}
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition"
                >
                  <option value="">Select Project Scope...</option>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Report Format</label>
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value as any)}
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition"
                >
                  <option value="PDF">ReportLab PDF Document (Executive Format)</option>
                  <option value="HTML">Jinja2 rendered HTML Report</option>
                  <option value="MD">Lightweight Markdown Report</option>
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
                  disabled={triggering}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2.5 rounded-xl text-sm transition flex items-center justify-center gap-1.5"
                >
                  {triggering ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" /> Queuing...
                    </>
                  ) : (
                    "Build Report"
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
