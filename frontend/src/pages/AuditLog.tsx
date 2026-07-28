import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ScrollText, User, Clock, ShieldCheck } from 'lucide-react';
import { getProjects, getAuditLogs } from '../api/client';
import { Project, AuditLog } from '../types';

export const AuditLogPage: React.FC = () => {
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  const activeProjectId = selectedProjectId || (projects[0]?.id ?? '');

  const { data: auditLogs = [], isLoading } = useQuery<AuditLog[]>({
    queryKey: ['auditLogs', activeProjectId],
    queryFn: () => (activeProjectId ? getAuditLogs(activeProjectId) : Promise.resolve([])),
    enabled: !!activeProjectId,
  });

  return (
    <div className="page-container">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Immutable Audit Log</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Cryptographically timestamped trail of all user actions, scope checks, and scan events</p>
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

      {isLoading ? (
        <div style={{ color: 'var(--text-secondary)' }}>Loading audit log records...</div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Timestamp (UTC)</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Entity Type</th>
                <th>Event Details</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map((log) => (
                <tr key={log.id}>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                      <User size={14} color="var(--accent-blue)" />
                      <strong style={{ fontSize: '0.85rem' }}>{log.actor}</strong>
                    </div>
                  </td>
                  <td>
                    <code style={{ fontSize: '0.8rem', background: '#0b0f19', color: 'var(--accent-green)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>
                      {log.action}
                    </code>
                  </td>
                  <td style={{ textTransform: 'capitalize' }}>{log.entity_type}</td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', maxWidth: '320px' }}>
                    <pre style={{ margin: 0, fontSize: '0.75rem', background: '#0b0f19', padding: '0.375rem', borderRadius: '4px', overflowX: 'auto' }}>
                      {JSON.stringify(log.details, null, 2)}
                    </pre>
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
