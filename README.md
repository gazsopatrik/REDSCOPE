# RedScope – Modular Authorized Vulnerability Assessment & Attack-Surface Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ed.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🛡️ Overview

**RedScope** is an enterprise-grade, modular vulnerability assessment and attack-surface analysis platform designed exclusively for **authorized security assessments, red-team engagements, and defensive vulnerability management**.

RedScope bridges the gap between raw port scanning and actionable security intelligence. It systematically maps authorized target infrastructure, correlates identified services against CVE vulnerability intelligence (with CVSS, EPSS, and CISA KEV data), calculates multi-factor risk scores, and suggests **strictly safe, non-destructive validation checks** that require explicit human approval before execution.

---

## ⚖️ Legal & Ethical Notice

> [!CAUTION]
> **AUTHORIZED USE ONLY**
> 
> RedScope is designed exclusively for authorized penetration testing, vulnerability assessments, security audits, and educational/laboratory environments. 
> 
> **Explicit written permission** from the system owner is strictly required prior to running scans or validations against any target host, IP, or domain. The end-user assumes full legal responsibility for compliance with all applicable local, national, and international cybersecurity laws and regulations.

---

## 🚀 Key Features

- **Strict Scope Boundaries**: Automatic pre-execution validation of targets against explicit inclusion (IPv4, IPv6, CIDR ranges, Hostnames) and exclusion rules. Hard-blocks out-of-scope targets.
- **Safe Subprocess Nmap Execution**: Controlled Nmap invocation using structured parameter arrays (no shell interpretation, zero injection risk).
- **Predefined Scan Profiles**: Standardized profiles including Quick Discovery, Standard Service Scan, Full TCP Scan, Selected Ports, and Common UDP.
- **Robust Defused XML Parsing**: Safe XML parsing of Nmap outputs extracting host status, ports, banners, SSL/TLS attributes, OS estimations, and CPE strings.
- **Service & Banner Normalization**: Rule-based normalization mapping inconsistent service banners into standardized CPE identifiers.
- **Vulnerability Intelligence Engine**: Automated correlation of normalized CPEs with CVE data, CVSS v3.1 scoring, EPSS probability, and CISA KEV (Known Exploited Vulnerabilities) status.
- **Dual-Scoring Engine**:
  - **Risk Score (0–100)**: Multi-factor scoring combining CVSS, EPSS, KEV status, match confidence, exposure level, and validation evidence.
  - **Confidence Score (0–100)**: Independent metric reflecting fingerprint reliability, banner exactness, and validation verification.
- **Safe Plugin-Based Validation Framework**: Plugin system supporting non-destructive checks (HTTP headers/TLS status, SSL certs, SSH algorithm audit, SMB dialect/signing checks).
- **Mandatory Approval Workflow**: Human-in-the-loop requirement before any active validation check is dispatched.
- **Multi-Format Executive Reporting**: Generate comprehensive audit-ready reports in HTML (responsive dark mode), JSON, and Markdown formats.
- **Immutable Audit Logging**: Every scope check, scan invocation, approval, validation execution, and report generation is logged with timestamp and actor details.

---

## 🚫 Anti-Exploitation Policy

RedScope is **NOT** an automated exploitation framework. The system strictly forbids and excludes:
- Automatic payload delivery or exploit execution
- Shell creation (reverse/bind shells)
- Credential dumping or brute-force attacks
- Data modification, deletion, or exfiltration
- Privilege escalation or lateral movement attempts
- Denial-of-service (DoS) or destructive stress tests

Core System Paradigm:
```text
Discover → Understand → Prioritize → Safely Validate → Report
```

---

## 🏗️ Architecture

RedScope is structured as a monorepo:

```text
redscope/
├── backend/                  # FastAPI Backend API Service
│   ├── app/
│   │   ├── api/              # REST Endpoints (Projects, Scopes, Targets, Scans, Findings, Validations, Reports)
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   ├── schemas/          # Pydantic v2 Input/Output Schemas
│   │   ├── scanners/         # Safe Subprocess Nmap Engine & XML Parser
│   │   ├── scope/            # Scope Validation & Exclusion Engine
│   │   ├── intelligence/     # CVE, CPE, EPSS & KEV Intelligence Providers
│   │   ├── scoring/          # Risk & Confidence Engine
│   │   ├── validators/       # Non-Destructive Plugin Framework
│   │   ├── reporting/        # HTML (Jinja2), JSON & Markdown Generators
│   │   └── security/         # Policy Enforcement & Input Sanitization
│   ├── alembic/              # Database Migration Scripts
│   └── tests/                # Pytest Unit, Integration & Security Tests
│
├── frontend/                 # React + TypeScript + Vite SPA
│   └── src/
│       ├── components/       # UI Components (Dark Security Theme)
│       ├── pages/            # Dashboard, Projects, Scans, Findings, Reports, Audit Log
│       └── api/              # API Client Integration
│
├── docs/                     # Detailed Project Documentation
│   ├── development-roadmap.md
│   ├── architecture.md
│   ├── safe-validation-policy.md
│   └── threat-model.md
│
├── docker-compose.yml        # Orchestration for PostgreSQL, Redis, Backend & Frontend
└── README.md
```

---

## 💻 Quick Start & Installation

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** & **npm**
- **Nmap 7.90+** (must be accessible in system PATH)
- **Docker & Docker Compose** (optional for containerized setup)

### 1. Local Setup

#### Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -e .
python -m app.main
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 2. Docker Compose Setup

```bash
docker-compose up --build -d
```
Access the application at `http://localhost:5173` (Frontend) and API docs at `http://localhost:8000/docs`.

---

## 📚 Documentation Index

- 📖 [Development Roadmap](docs/development-roadmap.md)
- 🏛️ [Architecture Specification](docs/architecture.md)
- 🔒 [Safe Validation Policy](docs/safe-validation-policy.md)
- 🛡️ [Threat Model & Security Controls](docs/threat-model.md)

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
