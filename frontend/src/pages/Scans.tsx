import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Activity, Play, Shield, Terminal, AlertCircle } from 'lucide-react';
import { getProjects, getAllTargets, getScans, createScan } from '../api/client';
import { Project, Target, Scan } from '../types';

export const ScansPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [showModal, setShowModal] = useState(false);
  const [targetId, setTargetId] = useState<string>('');
  const [profile, setProfile] = useState<string>('standard_service');
  const [customPorts, setCustomPorts] = useState<string>('');

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  const activeProjectId = selectedProjectId || (projects[0]?.id ?? '');

  const { data: allTargets = [] } = useQuery<Target[]>({
    queryKey: ['targets', 'all'],
    queryFn: getAllTargets,
  });

  const projectTargets = allTargets.filter((t) => !activeProjectId || t.project_id === activeProjectId);

  const { data: scans = [], isLoading } = useQuery<Scan[]>({
    queryKey: ['scans', activeProjectId],
    queryFn: () => (activeProjectId ? getScans(activeProjectId) : Promise.resolve([])),
    enabled: !!activeProjectId,
  });

  const launchMutation = useMutation({
    mutationFn: (data: { target_id: string; profile: string; custom_ports?: string }) =>
      createScan(activeProjectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scans', activeProjectId] });
      setShowModal(false);
      setTargetId('');
    },
  });

  const handleLaunch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetId || !activeProjectId) return;
    launchMutation.mutate({ target_id: targetId, profile, custom_ports: customPorts });
  };

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Nmap Discovery Scans</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Controlled subprocess execution with strict scope enforcement</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.625rem 1.25rem',
            backgroundColor: 'var(--accent-red)',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <Play size={18} />
          Launch New Scan
        </button>
      </div>

      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Select Project:</label>
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
        <div style={{ color: 'var(--text-secondary)' }}>Loading scan history...</div>
      ) : scans.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <Activity size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
          <h3>No Active or Completed Scans</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            Click "Launch New Scan" to initiate an authorized discovery task against a validated target.
          </p>
        </div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Profile</th>
                <th>Target ID</th>
                <th>Command Preview</th>
                <th>Status</th>
                <th>Hosts Discovered</th>
                <th>Started At</th>
              </tr>
            </thead>
            <tbody>
              {scans.map((s) => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 600, textTransform: 'capitalize' }}>{s.profile.replace('_', ' ')}</td>
                  <td><code>{s.target_id.slice(0, 8)}...</code></td>
                  <td>
                    <code style={{ fontSize: '0.75rem', background: '#0b0f19', padding: '0.25rem 0.5rem', borderRadius: '4px', color: 'var(--accent-green)' }}>
                      {s.command_preview || 'nmap -sV [target]'}
                    </code>
                  </td>
                  <td>
                    <span className="badge badge-low" style={{ background: s.status === 'completed' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)', color: s.status === 'completed' ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                      {s.status}
                    </span>
                  </td>
                  <td>{s.hosts?.length ?? 1} host(s)</td>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    {new Date(s.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="card" style={{ width: '520px', background: 'var(--bg-secondary)' }}>
            <h2 className="card-title">Launch Authorized Nmap Scan</h2>
            <form onSubmit={handleLaunch} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.375rem', color: 'var(--text-secondary)' }}>Select Authorized Target *</label>
                {projectTargets.length === 0 ? (
                  <div style={{ padding: '0.75rem', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '6px', color: 'var(--accent-red)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <AlertCircle size={16} /> No target hosts exist for this project yet. Please add a target on the Projects page first.
                  </div>
                ) : (
                  <select
                    required
                    value={targetId}
                    onChange={(e) => setTargetId(e.target.value)}
                    style={{ width: '100%', padding: '0.625rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-primary)', color: '#fff' }}
                  >
                    <option value="">-- Choose Target Host --</option>
                    {projectTargets.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.target_value} ({t.scope_status ? t.scope_status.toUpperCase() : 'PENDING'})
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.375rem', color: 'var(--text-secondary)' }}>Scan Profile *</label>
                <select
                  value={profile}
                  onChange={(e) => setProfile(e.target.value)}
                  style={{ width: '100%', padding: '0.625rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-primary)', color: '#fff' }}
                >
                  <option value="quick_discovery">Quick Discovery (Top 100 Ports)</option>
                  <option value="standard_service">Standard Service Scan (-sV intensity 5)</option>
                  <option value="full_tcp">Full TCP Scan (65,535 ports)</option>
                  <option value="selected_ports">Selected Custom Ports</option>
                  <option value="udp_common">UDP Common Services</option>
                </select>
              </div>

              {profile === 'selected_ports' && (
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.375rem', color: 'var(--text-secondary)' }}>Custom Port Specification</label>
                  <input
                    type="text"
                    value={customPorts}
                    onChange={(e) => setCustomPorts(e.target.value)}
                    placeholder="e.g. 22,80,443,8000-8080"
                    style={{ width: '100%', padding: '0.625rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-primary)', color: '#fff' }}
                  />
                </div>
              )}

              <div style={{ background: 'var(--bg-primary)', padding: '0.875rem', borderRadius: '6px', border: '1px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem', color: 'var(--accent-green)' }}>
                  <Shield size={14} />
                  <strong>Pre-Execution Scope Guard Active</strong>
                </div>
                Target will be re-validated against inclusion/exclusion rules immediately prior to socket binding.
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid var(--border-light)', color: '#fff', borderRadius: '6px', cursor: 'pointer' }}>Cancel</button>
                <button
                  type="submit"
                  disabled={!targetId}
                  style={{ padding: '0.5rem 1rem', background: targetId ? 'var(--accent-red)' : 'var(--text-muted)', border: 'none', color: '#fff', borderRadius: '6px', fontWeight: 600, cursor: targetId ? 'pointer' : 'not-allowed' }}
                >
                  Execute Scan
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
