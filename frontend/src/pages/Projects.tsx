import React, { useState, useEffect } from 'react';
import { projectService } from '../services/api';
import { Project } from '../types';
import { FolderPlus, Search, FolderGit2, Calendar, FileWarning } from 'lucide-react';

export const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const data = await projectService.list(search || undefined);
      setProjects(data);
    } catch (err) {
      setError("Failed to fetch projects database");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [search]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!name.trim()) return;

    try {
      await projectService.create({ name, description });
      setIsModalOpen(false);
      setName('');
      setDescription('');
      fetchProjects();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create project");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Vulnerability Auditing Scope</h2>
          <p className="text-sm text-cyber-muted font-mono">Create and register isolated projects for security scanning</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl font-semibold shadow-lg transition"
        >
          <FolderPlus className="w-5 h-5" /> Add Project Scope
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-4 top-3.5 w-5 h-5 text-cyber-muted" />
        <input
          type="text"
          placeholder="Search projects using PostgreSQL Full-Text Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-cyber-card border border-cyber-border rounded-xl py-3 pl-12 pr-4 text-sm text-white placeholder-cyber-muted outline-none focus:border-indigo-500 transition"
        />
      </div>

      {/* Projects Grid */}
      {loading && projects.length === 0 ? (
        <div className="text-center font-mono py-12 text-cyber-muted">Connecting to auditing ledger...</div>
      ) : projects.length === 0 ? (
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-12 text-center">
          <FolderGit2 className="w-12 h-12 text-cyber-muted mx-auto mb-4" />
          <h3 className="font-semibold text-white text-lg">No audit projects recorded</h3>
          <p className="text-sm text-cyber-muted mt-1">Start by registering a project target to capture credential scans.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {projects.map((proj) => (
            <div key={proj.id} className="bg-cyber-card border border-cyber-border hover:border-indigo-500/30 rounded-2xl p-6 flex flex-col justify-between group transition">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="bg-indigo-600/10 p-2 rounded-xl text-indigo-400 border border-indigo-500/10">
                    <FolderGit2 className="w-6 h-6" />
                  </div>
                  <h4 className="font-bold text-white group-hover:text-indigo-400 transition truncate">{proj.name}</h4>
                </div>
                <p className="text-sm text-cyber-muted line-clamp-3 leading-relaxed mb-6">
                  {proj.description || "No description provided for this scope project."}
                </p>
              </div>

              <div className="border-t border-cyber-border pt-4 flex justify-between items-center text-xs text-cyber-muted font-mono">
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5" />
                  {new Date(proj.created_at).toLocaleDateString()}
                </span>
                <span>ID: #{proj.id}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Project Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-6 z-50 animate-fade-in">
          <div className="bg-cyber-card border border-cyber-border rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
            <h3 className="text-lg font-bold text-white mb-4">Add Project Audit Scope</h3>
            
            {error && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-sm text-red-400">
                {error}
              </div>
            )}

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Scope Project Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. AWS Production Infrastructure"
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Description / Scope Boundaries</label>
                <textarea
                  rows={4}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Summarize target systems or organization boundary details"
                  className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition"
                />
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
                  Add Scope
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
