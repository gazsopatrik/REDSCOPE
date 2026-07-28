import React from 'react';
import { Settings as SettingsIcon, Shield, Server, Terminal, Lock } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="page-container">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>System Settings & Security Policy</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Core RedScope platform configuration and execution parameters</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <Server size={22} color="var(--accent-blue)" />
            <h2 className="card-title" style={{ margin: 0 }}>Backend Runtime Parameters</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem', fontSize: '0.9rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Environment</span>
              <strong>development</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>FastAPI Engine Version</span>
              <strong>0.1.0</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Database Driver</span>
              <strong>SQLite (aiosqlite) / PostgreSQL</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Task Queue</span>
              <strong>Redis (localhost:6379)</strong>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <Terminal size={22} color="var(--accent-green)" />
            <h2 className="card-title" style={{ margin: 0 }}>Scanner Engine Policies</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem', fontSize: '0.9rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Nmap Subprocess Exec</span>
              <strong style={{ color: 'var(--accent-green)' }}>Enabled (shell=False)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>XML Parser Security</span>
              <strong>defusedxml (XXE guarded)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Max Target CIDR</span>
              <strong>/20 (4,096 IPs)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Nmap Process Timeout</span>
              <strong>1800 seconds (30m)</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
