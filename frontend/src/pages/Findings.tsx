import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, ShieldAlert, CheckCircle, ExternalLink, Filter } from 'lucide-react';
import { getProjects, getFindings } from '../api/client';
import { Project, Finding } from '../types';

export const FindingsPage: React.FC = () => {
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  const activeProjectId = selectedProjectId || (projects[0]?.id ?? '');

  const { data: findings = [], isLoading } = useQuery<Finding[]>({
    queryKey: ['findings', activeProjectId],
    queryFn: () => (activeProjectId ? getFindings(activeProjectId) : Promise.resolve([])),
    enabled: !!activeProjectId,
  });

  const filteredFindings = findings.filter((f) =>
    severityFilter === 'all' ? true : f.severity.toLowerCase() === severityFilter.toLowerCase()
  );

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Vulnerability Findings</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Prioritized attack surface findings correlated with CVE, EPSS, & KEV intelligence</p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
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

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Filter size={16} color="var(--text-secondary)" />
          <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Severity:</label>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            style={{ padding: '0.5rem 1rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-secondary)', color: '#fff' }}
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div style={{ color: 'var(--text-secondary)' }}>Loading findings...</div>
      ) : filteredFindings.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <CheckCircle size={48} color="var(--accent-green)" style={{ marginBottom: '1rem' }} />
          <h3>No Matching Findings</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            No security findings matching the selected filters were identified.
          </p>
        </div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Risk Score</th>
                <th>Severity</th>
                <th>Confidence</th>
                <th>Finding Title</th>
                <th>Status</th>
                <th>Remediation</th>
              </tr>
            </thead>
            <tbody>
              {filteredFindings.map((f) => (
                <tr key={f.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                      <strong style={{ fontSize: '1.1rem', color: f.risk_score >= 80 ? 'var(--accent-red)' : f.risk_score >= 60 ? 'var(--accent-orange)' : 'var(--accent-yellow)' }}>
                        {f.risk_score}
                      </strong>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/100</span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge badge-${f.severity.toLowerCase()}`}>
                      {f.severity}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{f.confidence_score}/100</span>
                  </td>
                  <td style={{ fontWeight: 600 }}>
                    {f.title}
                  </td>
                  <td>
                    <span className="badge badge-low" style={{ background: 'rgba(139, 92, 246, 0.15)', color: 'var(--accent-purple)', borderColor: 'rgba(139, 92, 246, 0.3)' }}>
                      {f.status}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '280px' }}>
                    {f.remediation || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
