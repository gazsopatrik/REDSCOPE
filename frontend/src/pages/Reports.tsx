import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, Download, FileCode, FileSpreadsheet } from 'lucide-react';
import { getProjects } from '../api/client';
import { Project } from '../types';

export const ReportsPage: React.FC = () => {
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  const activeProjectId = selectedProjectId || (projects[0]?.id ?? '');

  return (
    <div className="page-container">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Executive Reports Center</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Generate and export audit-ready HTML, JSON, and Markdown security assessment reports</p>
      </div>

      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Project:</label>
        <select
          value={activeProjectId}
          onChange={(e) => setSelectedProjectId(e.target.value)}
          style={{ padding: '0.5rem 1rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-secondary)', color: '#fff' }}
        >
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      <div className="card">
        <h2 className="card-title">Generate New Report</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem', marginTop: '1rem' }}>
          <div style={{ padding: '1.25rem', background: 'var(--bg-primary)', borderRadius: '10px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
            <FileText size={32} color="var(--accent-red)" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ fontSize: '1.05rem', marginBottom: '0.375rem' }}>Responsive HTML Report</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Full executive report with Jinja2 dark theme styling, charts, and remediation guidelines.
            </p>
            <button
              style={{ padding: '0.5rem 1rem', background: 'var(--accent-red)', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem' }}
            >
              Generate HTML Report
            </button>
          </div>

          <div style={{ padding: '1.25rem', background: 'var(--bg-primary)', borderRadius: '10px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
            <FileCode size={32} color="var(--accent-blue)" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ fontSize: '1.05rem', marginBottom: '0.375rem' }}>Structured JSON Export</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Machine-readable structured JSON format for SIEM or vulnerability tracker integration.
            </p>
            <button
              style={{ padding: '0.5rem 1rem', background: 'var(--accent-blue)', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem' }}
            >
              Generate JSON Export
            </button>
          </div>

          <div style={{ padding: '1.25rem', background: 'var(--bg-primary)', borderRadius: '10px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
            <FileSpreadsheet size={32} color="var(--accent-purple)" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ fontSize: '1.05rem', marginBottom: '0.375rem' }}>Markdown Technical Report</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Clean plain-text Markdown document ideal for technical documentation repositories.
            </p>
            <button
              style={{ padding: '0.5rem 1rem', background: 'var(--accent-purple)', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem' }}
            >
              Generate Markdown Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
