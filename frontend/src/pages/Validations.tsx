import React from 'react';
import { CheckSquare, ShieldCheck, Lock, AlertCircle, Play } from 'lucide-react';

export const ValidationsPage: React.FC = () => {
  return (
    <div className="page-container">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Safe Validation Workbench</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Non-destructive security verification modules requiring mandatory human approval</p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <ShieldCheck size={24} color="var(--accent-green)" />
          <h2 className="card-title" style={{ margin: 0 }}>Human Approval & Anti-Exploitation Policy</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.5' }}>
          RedScope validators execute <strong>strictly non-destructive checks</strong> (HTTP header audits, TLS cert status, SSH banner queries, and SMB dialect checks).
          Automated exploitation, payload delivery, shells, and stress tests are hard-blocked by design.
        </p>

        <table className="table" style={{ marginTop: '1.5rem' }}>
          <thead>
            <tr>
              <th>Validator Module</th>
              <th>Target Service</th>
              <th>Risk Level</th>
              <th>Approval Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <div style={{ fontWeight: 600 }}>HTTP/HTTPS Security Header Audit</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>http_security_header_check</div>
              </td>
              <td><code>192.168.56.10:80 (http)</code></td>
              <td><span className="badge badge-low">LOW</span></td>
              <td>
                <span className="badge badge-medium" style={{ background: 'rgba(234, 179, 8, 0.15)', color: 'var(--accent-yellow)' }}>
                  AWAITING APPROVAL
                </span>
              </td>
              <td>
                <button
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.375rem',
                    padding: '0.4rem 0.875rem',
                    background: 'var(--accent-green)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  <Play size={14} /> Approve & Run
                </button>
              </td>
            </tr>

            <tr>
              <td>
                <div style={{ fontWeight: 600 }}>TLS/SSL Certificate & SAN Audit</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>tls_certificate_audit</div>
              </td>
              <td><code>192.168.56.10:443 (https)</code></td>
              <td><span className="badge badge-low">LOW</span></td>
              <td>
                <span className="badge badge-low" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-green)' }}>
                  PASSED / VERIFIED
                </span>
              </td>
              <td>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Verified</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
