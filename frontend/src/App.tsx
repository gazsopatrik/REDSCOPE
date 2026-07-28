import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Shield, LayoutDashboard, Target, Activity, AlertTriangle, CheckSquare, FileText, Settings, ScrollText } from 'lucide-react';
import { Dashboard } from './pages/Dashboard';
import { ProjectsPage } from './pages/Projects';
import { TargetsPage } from './pages/Targets';

const Sidebar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/projects', label: 'Projects', icon: Shield },
    { path: '/targets', label: 'Targets', icon: Target },
    { path: '/scans', label: 'Scans', icon: Activity },
    { path: '/findings', label: 'Findings', icon: AlertTriangle },
    { path: '/validations', label: 'Validations', icon: CheckSquare },
    { path: '/reports', label: 'Reports', icon: FileText },
    { path: '/audit-log', label: 'Audit Log', icon: ScrollText },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-icon">
          <Shield size={20} color="#fff" />
        </div>
        <div>
          <div className="brand-title">RedScope</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Vulnerability Platform
          </div>
        </div>
      </div>

      <nav className="nav-menu">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <header className="top-bar">
            <div className="top-bar-title">Authorized Vulnerability Assessment Platform</div>
            <div className="status-indicator">
              <span className="status-dot"></span>
              <span>System Operational</span>
            </div>
          </header>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/targets" element={<TargetsPage />} />
            <Route path="*" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
