import React, { useState, useEffect } from 'react';
import { findingService, projectService } from '../services/api';
import { Finding, Project } from '../types';
import { Bug, Search, Eye, AlertCircle, X, ShieldCheck, UserCheck } from 'lucide-react';

export const Findings: React.FC = () => {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [total, setTotal] = useState(0);

  // Filters
  const [selectedProject, setSelectedProject] = useState<number | ''>('');
  const [selectedSeverity, setSelectedSeverity] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [search, setSearch] = useState('');

  // Pagination
  const [limit] = useState(50);
  const [offset, setOffset] = useState(0);

  // Drawer Detail
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [remediationStatus, setRemediationStatus] = useState('');
  const [notes, setNotes] = useState('');

  const [loading, setLoading] = useState(false);

  const fetchDependencies = async () => {
    try {
      const projs = await projectService.list();
      setProjects(projs);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchFindings = async () => {
    setLoading(true);
    try {
      const data = await findingService.list({
        project_id: selectedProject || undefined,
        severity: selectedSeverity || undefined,
        status: selectedStatus || undefined,
        q: search || undefined,
        limit,
        offset
      });
      setFindings(data.findings);
      setTotal(data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDependencies();
  }, []);

  useEffect(() => {
    fetchFindings();
  }, [selectedProject, selectedSeverity, selectedStatus, search, offset]);

  const selectFindingForDetails = (finding: Finding) => {
    setSelectedFinding(finding);
    setRemediationStatus(finding.status);
    setNotes(finding.remediation_notes || '');
  };

  const handleUpdateRemediation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFinding) return;

    try {
      const updated = await findingService.update(selectedFinding.id, {
        status: remediationStatus,
        remediation_notes: notes
      });
      // Refresh finding details in drawer
      setSelectedFinding(updated);
      // Refresh findings table
      fetchFindings();
    } catch (err) {
      alert("Failed to update remediation status");
    }
  };

  const severityColor = (sev: string) => {
    switch (sev.upperCase?() || sev) {
      case 'CRITICAL': return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      case 'HIGH': return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      case 'MEDIUM': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      default: return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    }
  };

  return (
    <div className="space-y-6 relative h-full">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Active Discovered Exposures</h2>
        <p className="text-sm text-cyber-muted font-mono">Investigate compromised API credentials and code vulnerabilities</p>
      </div>

      {/* Filter and Search controls */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-cyber-card border border-cyber-border p-4 rounded-2xl">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Project Scope</label>
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value ? Number(e.target.value) : '')}
            className="w-full bg-gray-950 border border-cyber-border text-white text-sm rounded-xl py-2.5 px-4 outline-none focus:border-indigo-500"
          >
            <option value="">All Projects</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Severity</label>
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="w-full bg-gray-950 border border-cyber-border text-white text-sm rounded-xl py-2.5 px-4 outline-none focus:border-indigo-500"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Status</label>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="w-full bg-gray-950 border border-cyber-border text-white text-sm rounded-xl py-2.5 px-4 outline-none focus:border-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="CONFIRMED">Confirmed</option>
            <option value="REMEDIATED">Remediated</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Full-Text Search</label>
          <div className="relative">
            <Search className="absolute left-3 top-3 w-4 h-4 text-cyber-muted" />
            <input
              type="text"
              placeholder="Search finding details..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-gray-950 border border-cyber-border rounded-xl py-2 pl-9 pr-4 text-sm text-white outline-none focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Findings Table */}
      <div className="bg-cyber-card border border-cyber-border rounded-2xl overflow-hidden">
        <table className="w-full text-sm text-left border-collapse">
          <thead>
            <tr className="bg-gray-950/60 text-cyber-muted border-b border-cyber-border font-mono text-xs">
              <th className="p-4">ID</th>
              <th className="p-4">Secret Type</th>
              <th className="p-4">Severity</th>
              <th className="p-4">Risk</th>
              <th className="p-4">Location / Address</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody>
            {loading && findings.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center font-mono py-12 text-cyber-muted">Connecting findings database...</td>
              </tr>
            ) : findings.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center font-mono py-12 text-cyber-muted">No findings registered matching filters.</td>
              </tr>
            ) : (
              findings.map((f) => (
                <tr key={f.id} className="border-b border-cyber-border hover:bg-gray-900/30 transition">
                  <td className="p-4 font-mono text-xs text-cyber-muted">#{f.id}</td>
                  <td className="p-4">
                    <span className="font-semibold text-white">{f.secret_type_name}</span>
                    <span className="block text-[10px] text-cyber-muted font-mono mt-0.5">{f.masked_value}</span>
                  </td>
                  <td className="p-4">
                    <span className={`inline-block border rounded px-2.5 py-0.5 text-xs font-bold tracking-wider ${severityColor(f.severity)}`}>
                      {f.severity}
                    </span>
                  </td>
                  <td className="p-4 font-mono text-xs text-white">Score: {f.risk_score}</td>
                  <td className="p-4 font-mono text-xs text-cyber-muted truncate max-w-sm">
                    {f.file_path_or_url}
                    {f.line_number && <span className="text-indigo-400">:L{f.line_number}</span>}
                  </td>
                  <td className="p-4">
                    <span className={`inline-block rounded-full w-2 h-2 mr-2 ${f.status === 'REMEDIATED' || f.status === 'CLOSED' ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span className="font-mono text-xs font-semibold text-white">{f.status}</span>
                  </td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => selectFindingForDetails(f)}
                      className="inline-flex items-center gap-1 bg-gray-900 border border-cyber-border hover:bg-gray-800 text-cyber-muted hover:text-white px-2.5 py-1.5 rounded-lg text-xs transition"
                    >
                      <Eye className="w-3.5 h-3.5" /> View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Findings Remediation Detail Drawer */}
      {selectedFinding && (
        <div className="fixed inset-y-0 right-0 w-[550px] bg-cyber-card border-l border-cyber-border shadow-2xl p-6 overflow-y-auto z-50 animate-slide-in">
          <div className="flex justify-between items-center border-b border-cyber-border pb-4 mb-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Bug className="w-5 h-5 text-indigo-400" />
              Exposed Secret Context
            </h3>
            <button
              onClick={() => setSelectedFinding(null)}
              className="text-cyber-muted hover:text-white p-1 hover:bg-gray-800 rounded-lg transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-6">
            {/* Main Risk scores and severity details */}
            <div className="grid grid-cols-2 gap-4 bg-gray-950/60 p-4 rounded-xl border border-cyber-border text-sm">
              <div>
                <span className="text-xs text-cyber-muted font-mono block mb-1">Exposure Risk</span>
                <span className="font-semibold text-white">{selectedFinding.exposure_risk}</span>
              </div>
              <div>
                <span className="text-xs text-cyber-muted font-mono block mb-1">Compliance Risk</span>
                <span className="font-semibold text-white">{selectedFinding.compliance_risk}</span>
              </div>
              <div>
                <span className="text-xs text-cyber-muted font-mono block mb-1">Operational Risk</span>
                <span className="font-semibold text-white">{selectedFinding.operational_risk}</span>
              </div>
              <div>
                <span className="text-xs text-cyber-muted font-mono block mb-1">Composite Risk Score</span>
                <span className="font-semibold text-rose-500 font-mono">{selectedFinding.risk_score} / 100</span>
              </div>
            </div>

            {/* Finding location */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Target Vulnerability Location</h4>
              <p className="bg-gray-950 p-3 rounded-xl border border-cyber-border text-xs font-mono text-white break-all">
                {selectedFinding.file_path_or_url}
                {selectedFinding.line_number && <span className="text-indigo-400">#L{selectedFinding.line_number}</span>}
              </p>
            </div>

            {/* Evidence code block */}
            {selectedFinding.evidence_snippet && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-2">Vulnerable Code Context Evidence</h4>
                <pre className="bg-gray-950 p-4 rounded-xl border border-cyber-border text-xs text-indigo-300 font-mono overflow-x-auto whitespace-pre leading-relaxed">
                  <code>{selectedFinding.evidence_snippet}</code>
                </pre>
              </div>
            )}

            {/* Audit / Remediation Status Transition Forms */}
            <div className="border-t border-cyber-border pt-6">
              <h4 className="text-xs font-bold uppercase tracking-wider text-cyber-muted font-mono mb-4 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Remediation Workflow Transition
              </h4>

              <form onSubmit={handleUpdateRemediation} className="space-y-4">
                <div>
                  <label className="block text-xs text-cyber-muted font-mono mb-2">Workflow Status</label>
                  <select
                    value={remediationStatus}
                    onChange={(e) => setRemediationStatus(e.target.value)}
                    className="w-full bg-gray-950 border border-cyber-border text-white text-sm rounded-xl py-2 px-3 outline-none focus:border-indigo-500"
                  >
                    <option value="OPEN">Open (New Discovery)</option>
                    <option value="INVESTIGATING">Investigating (Triage)</option>
                    <option value="CONFIRMED">Confirmed (Awaiting Revocation)</option>
                    <option value="REMEDIATED">Remediated (Secret Revoked/Rotated)</option>
                    <option value="CLOSED">Closed (False Positive/Suppressed)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-cyber-muted font-mono mb-2">Audit & Resolution Notes</label>
                  <textarea
                    rows={4}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Log token revocation status, key rotation details, or audit evidence links."
                    className="w-full bg-gray-950 border border-cyber-border focus:border-indigo-500 rounded-xl py-2.5 px-4 text-white text-xs outline-none transition"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2.5 rounded-xl text-sm transition"
                >
                  Save Remediation Status
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
