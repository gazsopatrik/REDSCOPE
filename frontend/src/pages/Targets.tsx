import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Target as TargetIcon, Plus, RefreshCw, AlertCircle, Shield } from 'lucide-react';
import { getProjects, getAllTargets, createTarget, validateTargetScope } from '../api/client';
import { Project, Target as TargetType } from '../types';

export const TargetsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [showModal, setShowModal] = useState(false);
  const [targetValue, setTargetValue] = useState('');
  const [modalProjectId, setModalProjectId] = useState('');

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  const { data: allTargets = [], isLoading } = useQuery<TargetType[]>({
    queryKey: ['targets', 'all'],
    queryFn: getAllTargets,
  });

  const filteredTargets = allTargets.filter(
    (t) => !selectedProjectId || t.project_id === selectedProjectId
  );

  const addTargetMutation = useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: Partial<TargetType> }) =>
      createTarget(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['targets'] });
      setShowModal(false);
      setTargetValue('');
    },
  });

  const validateScopeMutation = useMutation({
    mutationFn: validateTargetScope,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['targets'] });
    },
  });

  const handleAddTarget = (e: React.FormEvent) => {
    e.preventDefault();
    const pid = modalProjectId || selectedProjectId || projects[0]?.id;
    if (!targetValue || !pid) return;
    addTargetMutation.mutate({ projectId: pid, data: { target_value: targetValue, target_type: 'ip' } });
  };

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Targets & Scope Validation</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Pre-execution verification of IP addresses, CIDR blocks, and Hostnames</p>
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
          <Plus size={18} />
          Add New Target
        </button>
      </div>

      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Filter by Project:</label>
        <select
          value={selectedProjectId}
          onChange={(e) => setSelectedProjectId(e.target.value)}
          style={{ padding: '0.5rem 1rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-secondary)', color: '#fff' }}
        >
          <option value="">All Security Projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div style={{ color: 'var(--text-secondary)' }}>Loading target hosts...</div>
      ) : filteredTargets.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <TargetIcon size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
          <h3>No Targets Registered</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            Click "Add New Target" to add target IPs or hostnames for scope verification.
          </p>
        </div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Target Host</th>
                <th>Resolved Address(es)</th>
                <th>Scope Status</th>
                <th>Scope Verification Details</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredTargets.map((t) => (
                <tr key={t.id}>
                  <td style={{ fontWeight: 600 }}>{t.target_value}</td>
                  <td>
                    {t.resolved_addresses?.length > 0 ? (
                      <code>{t.resolved_addresses.join(', ')}</code>
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Unresolved</span>
                    )}
                  </td>
                  <td>
                    <span className={`badge ${t.scope_status === 'allowed' ? 'badge-low' : 'badge-critical'}`} style={{ background: t.scope_status === 'allowed' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)', color: t.scope_status === 'allowed' ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                      {t.scope_status ? t.scope_status.toUpperCase() : 'PENDING'}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '320px' }}>
                    {t.scope_validation_message || 'Pending pre-execution evaluation'}
                  </td>
                  <td>
                    <button
                      onClick={() => validateScopeMutation.mutate(t.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.375rem',
                        padding: '0.375rem 0.75rem',
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-light)',
                        color: '#fff',
                        borderRadius: '6px',
                        fontSize: '0.8rem',
                        cursor: 'pointer',
                      }}
                    >
                      <RefreshCw size={14} /> Verify Scope
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="card" style={{ width: '450px', background: 'var(--bg-secondary)' }}>
            <h2 className="card-title">Add Target Host</h2>
            <form onSubmit={handleAddTarget} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.375rem', color: 'var(--text-secondary)' }}>Security Project *</label>
                <select
                  required
                  value={modalProjectId || selectedProjectId || projects[0]?.id || ''}
                  onChange={(e) => setModalProjectId(e.target.value)}
                  style={{ width: '100%', padding: '0.625rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-primary)', color: '#fff' }}
                >
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.375rem', color: 'var(--text-secondary)' }}>Target Host / IP Address *</label>
                <input
                  type="text"
                  required
                  value={targetValue}
                  onChange={(e) => setTargetValue(e.target.value)}
                  placeholder="e.g. 192.168.56.10 or server.lab.local"
                  style={{ width: '100%', padding: '0.625rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-primary)', color: '#fff' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid var(--border-light)', color: '#fff', borderRadius: '6px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '0.5rem 1rem', background: 'var(--accent-red)', border: 'none', color: '#fff', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}>Add Target</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
