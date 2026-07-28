# RedScope – System Architecture Specification

## 1. High-Level Architecture Overview

RedScope follows a modern decoupled monorepo architecture consisting of a Python FastAPI REST API backend, an async worker pipeline, a PostgreSQL/SQLite database, and a React + TypeScript single-page application frontend.

```text
┌─────────────────────────────────────────────────────────────┐
│                      React SPA Frontend                     │
│                (TypeScript / Vite / Tailwind CSS)           │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON REST API
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend Core                     │
│ ┌───────────────┐ ┌────────────────┐ ┌────────────────────┐ │
│ │ Scope Engine  │ │ Nmap Subprocess│ │ Intelligence Engine│ │
│ └───────────────┘ └────────────────┘ └────────────────────┘ │
│ ┌───────────────┐ ┌────────────────┐ ┌────────────────────┐ │
│ │ Risk Engine   │ │ Safe Validator │ │ Reporting Engine   │ │
│ └───────────────┘ └────────────────┘ └────────────────────┘ │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐  ┌───────────────────────────┐
│     PostgreSQL / SQLite      │  │     Redis / Task Queue    │
│  (SQLAlchemy 2.0 + Alembic)  │  │  (Background Scan Worker) │
└──────────────────────────────┘  └───────────────────────────┘
```

---

## 2. Core Domain Models & Schemas

### 2.1 Project Entity
Represents an authorized assessment boundary.
- `id`: UUID (Primary Key)
- `name`: String
- `description`: Text
- `client_name`: String
- `status`: Enum (`draft`, `active`, `paused`, `completed`, `archived`)
- `authorization_reference`: String (Document ID / ticket number)
- `rules_of_engagement`: Text
- `created_at`: Timestamp
- `updated_at`: Timestamp

### 2.2 Scope Entity
Defines permitted targets and explicit exclusions.
- `id`: UUID (Primary Key)
- `project_id`: UUID (Foreign Key -> Project)
- `scope_type`: Enum (`single_ip`, `cidr`, `hostname`, `domain`)
- `value`: String (e.g., `192.168.1.0/24` or `server.lab.internal`)
- `is_exclusion`: Boolean (default False)
- `enabled`: Boolean (default True)

### 2.3 Target Entity
A target host scheduled for scanning.
- `id`: UUID (Primary Key)
- `project_id`: UUID (Foreign Key -> Project)
- `target_value`: String
- `resolved_addresses`: JSON Array of IP strings
- `scope_status`: Enum (`pending`, `allowed`, `denied`, `resolution_failed`)
- `scope_validation_message`: String

### 2.4 Scan Entity
An Nmap discovery task.
- `id`: UUID (Primary Key)
- `project_id`: UUID (Foreign Key -> Project)
- `target_id`: UUID (Foreign Key -> Target)
- `profile`: Enum (`quick_discovery`, `standard_service`, `full_tcp`, `selected_ports`, `udp_common`)
- `status`: Enum (`queued`, `running`, `parsing`, `analyzing`, `completed`, `failed`, `cancelled`)
- `command_preview`: String
- `exit_code`: Integer
- `xml_output_path`: String

### 2.5 Host Entity
Host discovered during an Nmap scan.
- `id`: UUID (Primary Key)
- `scan_id`: UUID (Foreign Key -> Scan)
- `ip_address`: String
- `hostname`: String
- `mac_address`: String
- `vendor`: String
- `state`: String (`up`, `down`)
- `os_name`: String
- `os_accuracy`: Integer

### 2.6 Service Entity
Service running on a host port.
- `id`: UUID (Primary Key)
- `host_id`: UUID (Foreign Key -> Host)
- `protocol`: String (`tcp`, `udp`)
- `port`: Integer
- `state`: String (`open`, `closed`, `filtered`)
- `service_name`: String
- `product`: String
- `version`: String
- `tunnel`: String (`ssl`, `tls`, `none`)
- `cpe`: String
- `banner`: Text

### 2.7 Finding Entity
A correlated security issue or candidate vulnerability on a service.
- `id`: UUID (Primary Key)
- `service_id`: UUID (Foreign Key -> Service)
- `vulnerability_id`: String (CVE ID or internal vulnerability ID)
- `title`: String
- `description`: Text
- `status`: Enum (`suspected`, `candidate`, `validation_available`, `validation_pending`, `validated`, `not_vulnerable`, `false_positive`, `accepted_risk`, `remediated`)
- `severity`: Enum (`critical`, `high`, `medium`, `low`, `informational`)
- `risk_score`: Float (0-100)
- `confidence_score`: Float (0-100)
- `evidence`: JSON Object
- `remediation`: Text

### 2.8 Validation Entity
A safe non-destructive verification operation on a finding.
- `id`: UUID (Primary Key)
- `finding_id`: UUID (Foreign Key -> Finding)
- `validator_id`: String (Plugin identifier)
- `risk_level`: String (`low`, `informational`)
- `status`: Enum (`available`, `awaiting_approval`, `approved`, `running`, `passed`, `failed`, `inconclusive`)
- `requires_approval`: Boolean (always True)
- `approved_by`: String
- `approved_at`: Timestamp
- `result`: JSON Object

### 2.9 AuditLog Entity
Immutable record of all critical user and system actions.
- `id`: UUID (Primary Key)
- `timestamp`: Timestamp
- `actor`: String
- `action`: String
- `entity_type`: String
- `entity_id`: UUID
- `project_id`: UUID
- `details`: JSON Object

---

## 3. Technology Stack & Key Dependencies

### Backend
- **Python 3.12**
- **FastAPI**: Modern, fast web framework for building APIs.
- **Pydantic v2**: High-performance data validation.
- **SQLAlchemy 2.0**: Async ORM & SQL toolkit.
- **Alembic**: Database schema migration manager.
- **defusedxml**: Secure XML parsing package guarding against XXE.
- **httpx**: Async HTTP client for intelligence fetching and safe HTTP validation.
- **Jinja2**: Templating engine for HTML report generation.
- **pytest**: Test framework.
- **Ruff & mypy**: Code formatting, linting, and static type checking.

### Frontend
- **React 18 & TypeScript 5**
- **Vite**: Rapid frontend build tool.
- **TanStack Query (React Query)**: Async state management and API caching.
- **React Router 6**: Client-side routing.
- **Lucide Icons / Vanilla CSS**: Clean, dark-mode cybersecurity dashboard styling.
