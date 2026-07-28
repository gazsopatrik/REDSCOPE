import React from 'react';
import { Target as TargetIcon, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export const TargetsPage: React.FC = () => {
  return (
    <div className="page-container">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Targets & Scope Validation</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Pre-execution verification of IP addresses, CIDR blocks, and Hostnames</p>
      </div>

      <div className="card">
        <h2 className="card-title">Authorized Target Verification Workbench</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
          Targets must be validated against active inclusion and exclusion rules prior to launching Nmap scans.
        </p>

        <table className="table">
          <thead>
            <tr>
              <th>Target Value</th>
              <th>Resolved IP(s)</th>
              <th>Scope Status</th>
              <th>Verification Summary</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ fontWeight: 600 }}>192.168.56.10</td>
              <td><code>192.168.56.10</code></td>
              <td>
                <span className="badge badge-low" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-green)', borderColor: 'rgba(16, 185, 129, 0.3)' }}>
                  ALLOWED
                </span>
              </td>
              <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Target ALLOWED: All resolved IP(s) [192.168.56.10] are within authorized scope.
              </td>
            </tr>
            <tr>
              <td style={{ fontWeight: 600 }}>10.0.0.1</td>
              <td><code>10.0.0.1</code></td>
              <td>
                <span className="badge badge-critical">
                  DENIED
                </span>
              </td>
              <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Target DENIED: Resolved IP 10.0.0.1 is outside all permitted inclusion scopes.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
