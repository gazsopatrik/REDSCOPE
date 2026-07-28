import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Shield, CheckCircle, Target, X, Trash2, RefreshCw, Layers } from 'lucide-react';
import { getProjects, createProject, getScopes, createScope, deleteScope, getTargets, createTarget, validateTargetScope } from '../api/client';
import { Project, Scope, Target as TargetType } from '../types';

export const ProjectsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  // Form states for Create Project
  const [name, setName] = useState('');
  const [clientName, setClientName] = useState('');
  const [authRef, setAuthRef] = useState('');

  // Form states for Scope inside Project Drawer
  const [scopeType, setScopeType] = useState<'cidr' | 'single_ip' | 'hostname'>('cidr');
  const [scopeValue, setScopeValue] = useState('');
  const [isExclusion, setIsExclusion] = useState(false);

  // Form states for Target inside Project Drawer
  const [targetValue, setTargetValue] = useState('');

  const { data: projects = [], isLoading } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  // Queries for selected project scopes & targets
  const { data: projectScopes = [] } = useQuery<Scope[]>({
    queryKey: ['scopes', selectedProject?.id],
    queryFn: () => (selectedProject ? getScopes(selectedProject.id) : Promise.resolve([])),
    enabled: !!selectedProject,
  });

  const { data: projectTargets = [] } = useQuery<TargetType[]>({
    queryKey: ['targets', selectedProject?.id],
    queryFn: () => (selectedProject ? getTargets(selectedProject.id) : Promise.resolve([])),
    enabled: !!selectedProject,
  });

  // Mutations
  const createProjMutation = useMutation({
    mutationFn: createProject,
    onSuccess: (newProj) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setShowCreateModal(false);
      setName('');
      setClientName('');
      setAuthRef('');
      setSelectedProject(newProj);
    },
  });

  const addScopeMutation = useMutation({
    mutationFn: (data: Partial<Scope>) => createScope(selectedProject!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scopes', selectedProject?.id] });
      queryClient.invalidateQueries({ queryKey: ['targets', selectedProject?.id] });
      setScopeValue('');
    },
  });

  const deleteScopeMutation = useMutation({
    mutationFn: deleteScope,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scopes', selectedProject?.id] });
      queryClient.invalidateQueries({ queryKey: ['targets', selectedProject?.id] });
    },
  });

  const addTargetMutation = useMutation({
    mutationFn: (data: Partial<TargetType>) => createTarget(selectedProject!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['targets', selectedProject?.id] });
      queryClient.invalidateQueries({ queryKey: ['targets'] });
      setTargetValue('');
    },
  });

  const validateTargetMutation = useMutation({
    mutationFn: validateTargetScope,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['targets', selectedProject?.id] });
      queryClient.invalidateQueries({ queryKey: ['targets'] });
    },
  });

  const handleCreateProject = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    createProjMutation.mutate({
      name,
      client_name: clientName,
      authorization_reference: authRef,
    });
  };

  const handleAddScope = (e: React.FormEvent) => {
    e.preventDefault();
    if (!scopeValue || !selectedProject) return;
    addScopeMutation.mutate({
      scope_type: scopeType,
      value: scopeValue,
      is_exclusion: isExclusion,
    });
  };

  const handleAddTarget = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetValue || !selectedProject) return;
    addTargetMutation.mutate({
      target_value: targetValue,
      target_type: 'ip',
    });
  };

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Security Projects</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Click on any project to manage Scope rules, Targets, and execute Scope validations</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
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
          New Project
        </button>
      </div>

      {isLoading ? (
        <div style={{ color: 'var(--text-secondary)' }}>Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <Shield size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
          <h3>No Active Security Projects</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            Create your first authorized security assessment project to begin.
          </p>
        </div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Project Name</th>
                <th>Client / Org</th>
                <th>Auth Reference</th>
                <th>Status</th>
                <th>Created At</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr
                  key={p.id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => setSelectedProject(p)}
                >
                  <td style={{ fontWeight: 600, color: 'var(--accent-red)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Shield size={16} />
                      {p.name}
                    </div>
                  </td>
                  <td>{p.client_name || 'N/A'}</td>
                  <td>
                    <code style={{ fontSize: '0.8rem', background: '#1f2937', padding: '0.2rem 0.4rem', borderRadius: '4px' }}>
                      {p.authorization_reference || 'N/A'}
                    </code>
                  </td>
                  <td>
                    <span className="badge badge-medium">{p.status}</span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    {new Date(p.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedProject(p);
                      }}
                      style={{
                        padding: '0.375rem 0.75rem',
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-light)',
                        color: '#fff',
                        borderRadius: '6px',
                        fontSize: '0.8rem',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.375rem',
                      }}
                    >
                      <Layers size={14} /> Manage Scope & Targets
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* CREATE PROJECT MODAL */}
      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="card" style={{ width: '450px', background: 'var(--bg-secondary)' }}>
            <h2 className="card-title">Create Security Project</h2>
            <form onSubmit={handleCreateProject} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.375rem', color: 'var(--text-secondary)' }}>Project Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Acme Q3 Assessment"
                  style={{ width: '100%', padding: '0.625rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-primary)', color: '#fff' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.375rem', color: 'var(--text-secondary)' }}>Client Name</label>
                <input
                  type="text"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="e.g. Acme Corporation"
                  style={{ width: '100%', padding: '0.625rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-primary)', color: '#fff' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.375rem', color: 'var(--text-secondary)' }}>Authorization Reference</label>
                <input
                  type="text"
                  value={authRef}
                  onChange={(e) => setAuthRef(e.target.value)}
                  placeholder="e.g. SOW-2026-881"
                  style={{ width: '100%', padding: '0.625rem', borderRadius: '6px', border: '1px solid var(--border-light)', background: 'var(--bg-primary)', color: '#fff' }}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" onClick={() => setShowCreateModal(false)} style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid var(--border-light)', color: '#fff', borderRadius: '6px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '0.5rem 1rem', background: 'var(--accent-red)', border: 'none', color: '#fff', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}>Create Project</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* PROJECT WORKBENCH DRAWER */}
      {selectedProject && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'flex-end', zIndex: 100 }}>
          <div style={{ width: '650px', background: 'var(--bg-secondary)', height: '100%', overflowY: 'auto', padding: '2rem', borderLeft: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <Shield color="var(--accent-red)" size={24} />
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>{selectedProject.name}</h2>
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  Client: {selectedProject.client_name || 'Internal'} | Auth Ref: {selectedProject.authorization_reference || 'N/A'}
                </div>
              </div>
              <button
                onClick={() => setSelectedProject(null)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
              >
                <X size={24} />
              </button>
            </div>

            {/* SCOPE MANAGEMENT SECTION */}
            <div className="card" style={{ background: 'var(--bg-primary)' }}>
              <h3 className="card-title" style={{ fontSize: '1.1rem', marginBottom: '0.75rem' }}>Authorized Scope Rules</h3>
              
              <form onSubmit={handleAddScope} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                <select
                  value={scopeType}
                  onChange={(e: any) => setScopeType(e.target.value)}
                  style={{ padding: '0.5rem', borderRadius: '6px', background: 'var(--bg-card)', border: '1px solid var(--border-light)', color: '#fff' }}
                >
                  <option value="cidr">CIDR Range</option>
                  <option value="single_ip">Single IP</option>
                  <option value="hostname">Hostname</option>
                </select>

                <input
                  type="text"
                  required
                  placeholder="e.g. 192.168.1.0/24"
                  value={scopeValue}
                  onChange={(e) => setScopeValue(e.target.value)}
                  style={{ flex: 1, minWidth: '150px', padding: '0.5rem', borderRadius: '6px', background: 'var(--bg-card)', border: '1px solid var(--border-light)', color: '#fff' }}
                />

                <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  <input
                    type="checkbox"
                    checked={isExclusion}
                    onChange={(e) => setIsExclusion(e.target.checked)}
                  />
                  Exclusion Rule
                </label>

                <button type="submit" style={{ padding: '0.5rem 0.875rem', background: 'var(--accent-red)', border: 'none', color: '#fff', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}>
                  Add Scope Rule
                </button>
              </form>

              {projectScopes.length === 0 ? (
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No scope rules defined. Add a CIDR or IP to authorize scanning.</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {projectScopes.map((s) => (
                    <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0.75rem', background: 'var(--bg-card)', borderRadius: '6px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span className={`badge ${s.is_exclusion ? 'badge-critical' : 'badge-low'}`}>
                          {s.is_exclusion ? 'EXCLUSION' : 'INCLUSION'}
                        </span>
                        <code>{s.value}</code>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>({s.scope_type})</span>
                      </div>
                      <button
                        onClick={() => deleteScopeMutation.mutate(s.id)}
                        style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* TARGETS MANAGEMENT SECTION */}
            <div className="card" style={{ background: 'var(--bg-primary)' }}>
              <h3 className="card-title" style={{ fontSize: '1.1rem', marginBottom: '0.75rem' }}>Project Target Hosts</h3>
              
              <form onSubmit={handleAddTarget} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                <input
                  type="text"
                  required
                  placeholder="Target IP / Hostname (e.g. 192.168.1.50)"
                  value={targetValue}
                  onChange={(e) => setTargetValue(e.target.value)}
                  style={{ flex: 1, padding: '0.5rem', borderRadius: '6px', background: 'var(--bg-card)', border: '1px solid var(--border-light)', color: '#fff' }}
                />
                <button type="submit" style={{ padding: '0.5rem 0.875rem', background: 'var(--accent-blue)', border: 'none', color: '#fff', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}>
                  Add Target
                </button>
              </form>

              {projectTargets.length === 0 ? (
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No target hosts added yet.</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {projectTargets.map((t) => (
                    <div key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.625rem', background: 'var(--bg-card)', borderRadius: '6px' }}>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{t.target_value}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.scope_validation_message || 'Scope check pending'}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span className={`badge ${t.scope_status === 'allowed' ? 'badge-low' : 'badge-critical'}`} style={{ background: t.scope_status === 'allowed' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)', color: t.scope_status === 'allowed' ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                          {t.scope_status ? t.scope_status.toUpperCase() : 'PENDING'}
                        </span>
                        <button
                          onClick={() => validateTargetMutation.mutate(t.id)}
                          title="Re-verify Scope"
                          style={{ background: 'transparent', border: '1px solid var(--border-light)', color: '#fff', padding: '0.25rem 0.5rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                        >
                          <RefreshCw size={12} /> Check Scope
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
