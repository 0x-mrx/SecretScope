export interface User {
  id: number;
  email: string;
  role: 'ADMIN' | 'ANALYST' | 'AUDITOR';
  is_active: boolean;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

export interface Asset {
  id: number;
  project_id: number;
  type: 'WEBSITE' | 'REPOSITORY' | 'FILE_PATH';
  target_url_or_path: string;
  schedule_cron?: string;
  status: 'ACTIVE' | 'INACTIVE';
  last_scanned_at?: string;
  created_at: string;
}

export interface Finding {
  id: number;
  scan_id: number;
  secret_type_name: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'OPEN' | 'INVESTIGATING' | 'CONFIRMED' | 'REMEDIATED' | 'CLOSED';
  exposure_risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  compliance_risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  operational_risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_score: number;
  file_path_or_url: string;
  line_number?: number;
  masked_value: string;
  evidence_snippet?: string;
  remediation_notes?: string;
  owner_id?: number;
  resolved_at?: string;
  created_at: string;
}

export interface Report {
  id: number;
  project_id: number;
  type: 'PDF' | 'HTML' | 'MD';
  file_path: string;
  summary_stats?: string;
  created_at: string;
}

export interface DashboardData {
  severity_distribution: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  asset_metrics: {
    WEBSITE: number;
    REPOSITORY: number;
    FILE_PATH: number;
    TOTAL: number;
  };
  mttr_hours: number;
  sla_compliance_percentage: number;
  open_findings_trend: Array<{ date: string; count: number }>;
  recent_activity: Array<{ action: string; details: string; timestamp: string }>;
}
