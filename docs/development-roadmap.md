# RedScope – Development Roadmap & Execution Tracker

This document outlines the detailed 9-phase development plan for RedScope. Every phase contains explicit deliverables, verification criteria, and security requirements.

---

## 📌 Development Phases Overview

```text
Phase 1: Project Foundation & Core Infrastructure
   ↓
Phase 2: Project, Scope & Target Management Engine
   ↓
Phase 3: Safe Nmap Scanner Subprocess Engine & XML Parsing
   ↓
Phase 4: Service Normalization & Vulnerability Intelligence Pipeline
   ↓
Phase 5: Dual Risk & Confidence Scoring System
   ↓
Phase 6: Plugin-Based Safe Validator Framework & Approval Workflow
   ↓
Phase 7: Executive & Technical Multi-Format Reporting Engine
   ↓
Phase 8: React Frontend Application & Dashboard UI
   ↓
Phase 9: Quality Assurance, Security Audit & Seed Script Integration
```

---

## 🛠️ Detailed Phase Breakdowns

### Phase 1: Project Foundation & Infrastructure
- [x] Repository initialization & Git remote link setup.
- [x] Master documentation creation (`README.md`, `docs/*.md`).
- [ ] Backend setup: Python FastAPI application structure, `pyproject.toml`, Ruff, mypy, pytest.
- [ ] Database setup: SQLAlchemy 2.0 async engine configuration & Alembic migrations setup.
- [ ] Environment management: `.env.example` and Pydantic Settings class (`app/config.py`).
- [ ] Core API Endpoint: `/api/health` returning system status, database connection state, and Nmap availability.
- [ ] Docker infrastructure: `docker-compose.yml` for PostgreSQL, Redis, Backend API, and Frontend SPA.

### Phase 2: Project, Scope & Target Engine
- [ ] SQLAlchemy ORM Models: `Project`, `Scope`, `Target`, `AuditLog`.
- [ ] Scope Validator Component (`app/scope/validator.py`):
  - IPv4 and IPv6 address parsing (`ipaddress` library).
  - CIDR block calculation and size verification (max target threshold).
  - Hostname resolution & DNS rebinding defense.
  - Inclusion and Exclusion matching algorithm.
- [ ] Scope Enforcement API:
  - `POST /api/projects/{id}/scopes`
  - `POST /api/projects/{id}/targets`
  - `POST /api/targets/{id}/validate-scope`
- [ ] Immutable Audit Logging mechanism (`app/models/audit_log.py`).

### Phase 3: Nmap Scanner Engine & XML Parser
- [ ] Safe Subprocess Command Builder (`app/scanners/nmap_runner.py`):
  - Argument array construction (no string formatting, no `shell=True`).
  - Predefined profile enforcement: `Quick Discovery`, `Standard Service Scan`, `Full TCP Scan`, `Selected Ports`, `UDP Common`.
  - Process timeout and execution monitoring.
- [ ] XML Parser (`app/scanners/nmap_parser.py`):
  - Safe parsing using `defusedxml.ElementTree`.
  - Extraction of host states, IP/MAC addresses, vendor info, port numbers, protocols, service names, products, versions, CPE strings, extra info, and OS fingerpints.
- [ ] Scan Storage & API Endpoints:
  - `POST /api/projects/{id}/scans`
  - `GET /api/scans/{id}`
  - `POST /api/scans/{id}/cancel`

### Phase 4: Service Normalization & Vulnerability Intelligence
- [ ] Service Banner Normalizer (`app/intelligence/cpe_matcher.py`):
  - Standardizing vendor, product, and version formats into CPE 2.3 identifiers.
  - Assigning match confidence (`exact`, `high`, `medium`, `low`, `unknown`).
- [ ] Intelligence Providers (`app/intelligence/`):
  - `CVEProvider`: NVD / local cache correlation for CVE IDs, CVSS scores, descriptions, CWE IDs.
  - `EPSSProvider`: Exploit Prediction Scoring System score and percentile integration.
  - `KEVProvider`: CISA Known Exploited Vulnerabilities catalog matching.
- [ ] Finding Candidate Generator (`app/services/analysis_service.py`).

### Phase 5: Dual Risk & Confidence Scoring System
- [ ] Risk Engine (`app/scoring/risk_engine.py`):
  - 0–100 calculated score based on weighted factors:
    - CVSS score (25 pts)
    - EPSS score (20 pts)
    - CISA KEV status (15 pts)
    - CPE Match Confidence (15 pts)
    - Exposure level (10 pts)
    - Exploit Maturity metadata (5 pts)
    - Validation Evidence (10 pts)
  - Priority mapping: Critical (80-100), High (60-79), Medium (40-59), Low (20-39), Informational (0-19).
- [ ] Confidence Engine (`app/scoring/confidence.py`):
  - Independent 0–100 score quantifying detection accuracy.
- [ ] Transparent human-readable explanation builder for every score calculation.

### Phase 6: Plugin-Based Safe Validator Framework
- [ ] Abstract Base Validator Interface (`app/validators/base.py`).
- [ ] Validator Plugin Registry (`app/validators/registry.py`).
- [ ] Implemented Non-Destructive Checkers:
  - **HTTP/HTTPS Validator**: Security headers, Server banner, TLS redirect, status code.
  - **TLS/SSL Validator**: Certificate validity, expiration date, self-signed detection, cipher suite audit.
  - **SSH Validator**: Banner analysis, supported key exchange algorithms, weak cipher identification.
  - **SMB Validator**: SMB dialect detection, SMBv1 flag check, guest/anonymous share access check.
- [ ] Human Approval Workflow & API:
  - `POST /api/findings/{id}/validations`
  - `POST /api/validations/{id}/approve`
  - `POST /api/validations/{id}/run`

### Phase 7: Multi-Format Reporting Engine
- [ ] Report Generators (`app/reporting/`):
  - HTML Generator: Responsive dark-themed report with charts, executive summary, findings table, evidence breakdown, and remediation guide (via Jinja2).
  - JSON Generator: Machine-readable structured export.
  - Markdown Generator: Clean plain-text documentation export.
- [ ] Reporting API:
  - `POST /api/projects/{id}/reports`
  - `GET /api/reports/{id}/download`

### Phase 8: React Frontend Application & UI
- [ ] UI Component System: Modern dark-mode palette, typography (Inter/Roboto), dynamic stat cards, status badges, progress bars, tables, modal dialogs.
- [ ] Views & Navigation:
  - Dashboard Page (Key metrics, risk charts, quick actions)
  - Projects Page & Project Details View
  - Targets & Scope Manager View
  - Scan Manager & Real-Time Progress View
  - Findings Table & Detailed Vulnerability Inspector
  - Safe Validation Approval & Run Workbench
  - Reports Center
  - Audit Log Viewer

### Phase 9: Quality Assurance & Seed Data
- [ ] Automated Test Suites (`pytest`):
  - Scope validator edge-case tests (IPv4, IPv6, CIDR, DNS rebinding, exclusions).
  - Nmap parser unit tests using mock XML fixtures.
  - Risk engine score calculation assertions.
  - Validator plugin execution tests.
  - API endpoint integration tests.
- [ ] Seed Data Script (`scripts/seed_demo_data.py`):
  - Pre-populates a "Demo Lab" project with simulated scope, targets, scans, services, findings, and validations marked as `DEMO DATA – NOT A REAL SECURITY ASSESSMENT`.
- [ ] Documentation polish & final verification.
