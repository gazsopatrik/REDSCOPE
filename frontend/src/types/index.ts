export type ProjectStatus = 'draft' | 'active' | 'paused' | 'completed' | 'archived';
export type ScopeType = 'single_ip' | 'cidr' | 'hostname' | 'domain';
export type ScopeStatus = 'pending' | 'allowed' | 'denied' | 'resolution_failed';
export type ScanProfile = 'quick_discovery' | 'standard_service' | 'full_tcp' | 'selected_ports' | 'udp_common';
export type ScanStatus = 'queued' | 'running' | 'parsing' | 'analyzing' | 'completed' | 'failed' | 'cancelled';
export type FindingSeverity = 'critical' | 'high' | 'medium' | 'low' | 'informational';
export type FindingStatus = 'suspected' | 'candidate' | 'validation_available' | 'validation_pending' | 'validated' | 'not_vulnerable' | 'false_positive' | 'accepted_risk' | 'remediated';
export type ValidationStatus = 'available' | 'awaiting_approval' | 'approved' | 'running' | 'passed' | 'failed' | 'inconclusive' | 'blocked' | 'cancelled';
export type ReportFormat = 'html' | 'json' | 'markdown';

export interface Project {
  id: string;
  name: string;
  description?: string;
  client_name?: string;
  status: ProjectStatus;
  authorization_reference?: string;
  rules_of_engagement?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Scope {
  id: string;
  project_id: string;
  scope_type: ScopeType;
  value: string;
  description?: string;
  is_exclusion: boolean;
  enabled: boolean;
  created_at: string;
}

export interface Target {
  id: string;
  project_id: string;
  target_value: string;
  resolved_addresses: string[];
  target_type: string;
  scope_status: ScopeStatus;
  scope_validation_message?: string;
  created_at: string;
  last_scanned_at?: string;
}

export interface Service {
  id: string;
  host_id: string;
  protocol: string;
  port: number;
  state: string;
  service_name?: string;
  product?: string;
  version?: string;
  cpe?: string;
  confidence?: number;
}

export interface Host {
  id: string;
  scan_id: string;
  ip_address: string;
  hostname?: string;
  state: string;
  os_name?: string;
  services: Service[];
}

export interface Scan {
  id: string;
  project_id: string;
  target_id: string;
  profile: ScanProfile;
  status: ScanStatus;
  command_preview?: string;
  created_by: string;
  created_at: string;
  hosts: Host[];
}

export interface Finding {
  id: string;
  service_id: string;
  title: string;
  description?: string;
  status: FindingStatus;
  severity: FindingSeverity;
  risk_score: number;
  confidence_score: number;
  remediation?: string;
  created_at: string;
}

export interface Validation {
  id: string;
  finding_id: string;
  validator_id: string;
  validator_name: string;
  risk_level: string;
  status: ValidationStatus;
  requires_approval: boolean;
  approved_by?: string;
  evidence?: Record<string, any>;
  error_message?: string;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  entity_type: string;
  entity_id?: string;
  details?: Record<string, any>;
}
