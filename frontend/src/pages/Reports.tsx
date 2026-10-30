import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AlertCircle, Download, FileCode, FileSpreadsheet, FileText } from 'lucide-react';
import {
  createReport,
  getProjects,
  getReportDownloadUrl,
  getReports,
  Report,
} from '../api/client';
import { Project, ReportFormat } from '../types';

export const ReportsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  const activeProjectId = selectedProjectId || (projects[0]?.id ?? '');
  const activeProject = projects.find((project) => project.id === activeProjectId);

  const { data: reports = [], isLoading: reportsLoading, isError: reportsError, error: reportsFetchError, refetch: refetchReports } = useQuery<Report[]>({
    queryKey: ['reports', activeProjectId],
    queryFn: () => getReports(activeProjectId),
    enabled: Boolean(activeProjectId),
  });

  const generateMutation = useMutation({
    mutationFn: (format: ReportFormat) => createReport(activeProjectId, {
      title: `${activeProject?.name ?? 'Security'} Assessment`,
      format,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports', activeProjectId] });
    },
  });

  const reportOptions: Array<{
    format: ReportFormat;
    title: string;
    description: string;
    label: string;
    color: string;
    icon: React.ReactNode;
  }> = [
    {
      format: 'html',
      title: 'Responsive HTML Report',
      description: 'Full executive report with a dark theme, findings, and remediation guidance.',
      label: 'Generate HTML Report',
      color: 'var(--accent-red)',
      icon: <FileText size={32} color="var(--accent-red)" />,
    },
    {
      format: 'json',
      title: 'Structured JSON Export',
      description: 'Machine-readable structured JSON for SIEM or vulnerability tracker integration.',
      label: 'Generate JSON Export',
      color: 'var(--accent-blue)',
      icon: <FileCode size={32} color="var(--accent-blue)" />,
    },
    {
      format: 'markdown',
      title: 'Markdown Technical Report',
      description: 'Plain-text Markdown suitable for technical documentation repositories.',
      label: 'Generate Markdown Report',
      color: 'var(--accent-purple)',
      icon: <FileSpreadsheet size={32} color="var(--accent-purple)" />,
    },
  ];

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
          onChange={(event) => setSelectedProjectId(event.target.value)}
          disabled={projects.length === 0}
          style={{ padding: '0.5rem 1rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-secondary)', color: '#fff' }}
        >
          {projects.length === 0 && <option value="">No projects available</option>}
          {projects.map((project) => (
            <option key={project.id} value={project.id}>{project.name}</option>
          ))}
        </select>
      </div>

      {generateMutation.isError && (
        <div style={{ marginBottom: '1rem', padding: '0.75rem', background: 'rgba(239,68,68,0.15)', border: '1px solid var(--accent-red)', borderRadius: '6px', color: 'var(--accent-red)' }}>
          <AlertCircle size={16} style={{ display: 'inline', marginRight: '0.375rem', verticalAlign: 'middle' }} />
          {(generateMutation.error as any)?.response?.data?.detail || (generateMutation.error as Error)?.message || 'Report generation failed.'}
        </div>
      )}

      <div className="card">
        <h2 className="card-title">Generate New Report</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem', marginTop: '1rem' }}>
          {reportOptions.map((option) => (
            <div key={option.format} style={{ padding: '1.25rem', background: 'var(--bg-primary)', borderRadius: '10px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
              <div style={{ marginBottom: '0.75rem' }}>{option.icon}</div>
              <h3 style={{ fontSize: '1.05rem', marginBottom: '0.375rem' }}>{option.title}</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                {option.description}
              </p>
              <button
                type="button"
                onClick={() => generateMutation.mutate(option.format)}
                disabled={!activeProjectId || generateMutation.isPending}
                style={{ padding: '0.5rem 1rem', background: option.color, color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: activeProjectId && !generateMutation.isPending ? 'pointer' : 'not-allowed', fontSize: '0.85rem', opacity: activeProjectId ? 1 : 0.6 }}
              >
                {generateMutation.isPending && generateMutation.variables === option.format
                  ? 'Generating...'
                  : option.label}
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h2 className="card-title">Generated Reports</h2>
        {reportsLoading ? (
          <p style={{ color: 'var(--text-secondary)' }}>Loading reports...</p>
        ) : reportsError ? (
          <div role="alert" style={{ color: 'var(--accent-red)' }}>
            <p>Could not load reports: {(reportsFetchError as Error)?.message ?? 'Unknown error'}</p>
            <button type="button" onClick={() => void refetchReports()}>Retry</button>
          </div>
        ) : reports.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)' }}>No reports have been generated for this project.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Format</th>
                <th>Created</th>
                <th>Download</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((report) => (
                <tr key={report.id}>
                  <td>{report.title}</td>
                  <td style={{ textTransform: 'uppercase' }}>{report.format}</td>
                  <td>{new Date(report.created_at).toLocaleString()}</td>
                  <td>
                    <a
                      href={getReportDownloadUrl(report.id)}
                      style={{ color: 'var(--accent-blue)', display: 'inline-flex', alignItems: 'center', gap: '0.375rem' }}
                    >
                      <Download size={16} /> Download
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
