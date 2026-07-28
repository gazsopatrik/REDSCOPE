import React from 'react';
import { Shield, Target, Activity, AlertTriangle, CheckCircle, FileText } from 'lucide-react';

export const Dashboard: React.FC = () => {
  return (
    <div className="page-container">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          Security Assessment Dashboard
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Authorized Attack Surface & Vulnerability Management Overview
        </p>
      </div>

      <div className="grid-metrics">
        <div className="stat-card">
          <div className="stat-header">
            <span>Active Projects</span>
            <Shield size={18} color="var(--accent-blue)" />
          </div>
          <div className="stat-value">1</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>Scoped Targets</span>
            <Target size={18} color="var(--accent-purple)" />
          </div>
          <div className="stat-value">2</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>Total Scans</span>
            <Activity size={18} color="var(--accent-green)" />
          </div>
          <div className="stat-value">0</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>Critical Findings</span>
            <AlertTriangle size={18} color="var(--accent-red)" />
          </div>
          <div className="stat-value" style={{ color: 'var(--accent-red)' }}>0</div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">System Status & Environment</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          <div style={{ padding: '1rem', background: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <CheckCircle size={16} color="var(--accent-green)" />
              <strong style={{ fontSize: '0.95rem' }}>Backend API Status</strong>
            </div>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>FastAPI Engine Online (v0.1.0)</span>
          </div>

          <div style={{ padding: '1rem', background: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Shield size={16} color="var(--accent-blue)" />
              <strong style={{ fontSize: '0.95rem' }}>Scope Engine</strong>
            </div>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Pre-Execution Verification Enabled</span>
          </div>

          <div style={{ padding: '1rem', background: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <FileText size={16} color="var(--accent-purple)" />
              <strong style={{ fontSize: '0.95rem' }}>Audit Logging</strong>
            </div>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Immutable Event Trail Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};
