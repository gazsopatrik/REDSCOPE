#!/usr/bin/env python3
"""
RedScope Demo Lab Data Seeder
Populates database with sample authorized projects, scopes, targets, scans, and findings for local testing.
"""

import asyncio
import sys
from pathlib import Path

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import AsyncSessionLocal, Base, engine
from app.models import (
    AuditLog,
    Finding,
    FindingSeverity,
    FindingStatus,
    Host,
    Project,
    ProjectStatus,
    Scan,
    ScanProfile,
    ScanStatus,
    Scope,
    ScopeStatus,
    ScopeType,
    Service,
    Target,
    TargetType,
    Validation,
    ValidationStatus,
    Vulnerability,
)


async def seed_data():
    print("[+] Initializing RedScope Database Tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        print("[+] Seeding Demo Security Assessment Project...")

        # 1. Demo Project
        project = Project(
            name="Demo Security Assessment Lab",
            description="Simulated authorized security audit laboratory environment.",
            client_name="Internal Security Lab",
            status=ProjectStatus.ACTIVE,
            authorization_reference="LAB-AUTH-2026-DEMO",
            rules_of_engagement="Non-destructive scanning and safe validation only.",
        )
        session.add(project)
        await session.flush()

        # 2. Scope Rules
        scope_inc = Scope(
            project_id=project.id,
            scope_type=ScopeType.CIDR,
            value="192.168.56.0/24",
            description="Authorized Lab Network Range",
            is_exclusion=False,
        )
        scope_ex = Scope(
            project_id=project.id,
            scope_type=ScopeType.SINGLE_IP,
            value="192.168.56.254",
            description="Excluded Gateway Device",
            is_exclusion=True,
        )
        session.add_all([scope_inc, scope_ex])
        await session.flush()

        # 3. Targets
        target_allowed = Target(
            project_id=project.id,
            target_value="192.168.56.10",
            resolved_addresses=["192.168.56.10"],
            target_type=TargetType.IP,
            scope_status=ScopeStatus.ALLOWED,
            scope_validation_message="Target ALLOWED: All resolved IP(s) [192.168.56.10] are within authorized scope.",
        )
        session.add(target_allowed)
        await session.flush()

        # 4. Demo Scan
        scan = Scan(
            project_id=project.id,
            target_id=target_allowed.id,
            profile=ScanProfile.STANDARD_SERVICE,
            status=ScanStatus.COMPLETED,
            command_preview="nmap -sV --version-intensity 5 -O -oX scan_demo.xml 192.168.56.10",
            exit_code=0,
        )
        session.add(scan)
        await session.flush()

        # 5. Host & Services
        host = Host(
            scan_id=scan.id,
            ip_address="192.168.56.10",
            hostname="demo-server.lab.local",
            mac_address="00:11:22:33:44:55",
            vendor="VirtualBox",
            state="up",
            os_name="Ubuntu Linux 22.04",
        )
        session.add(host)
        await session.flush()

        svc_http = Service(
            host_id=host.id,
            protocol="tcp",
            port=80,
            state="open",
            service_name="http",
            product="nginx",
            version="1.22.1",
            cpe="cpe:2.3:a:nginx:nginx:1.22.1:*:*:*:*:*:*:*",
        )
        svc_ssh = Service(
            host_id=host.id,
            protocol="tcp",
            port=22,
            state="open",
            service_name="ssh",
            product="OpenSSH",
            version="7.2p1",
            cpe="cpe:2.3:a:openbsd:openssh:7.2p1:*:*:*:*:*:*:*",
        )
        session.add_all([svc_http, svc_ssh])
        await session.flush()

        # 6. Vulnerabilities & Findings
        vuln_cve = Vulnerability(
            cve_id="CVE-2023-44487",
            title="HTTP/2 Rapid Reset Denial of Service",
            description="The HTTP/2 protocol allows a high volume of requests with RST_STREAM frames, resulting in significant CPU utilization.",
            cvss_score=7.5,
            cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
            severity="high",
            cwe_ids=["CWE-400"],
            known_exploited=True,
            epss_score=0.85,
            epss_percentile=0.92,
        )
        session.add(vuln_cve)
        await session.flush()

        finding = Finding(
            service_id=svc_http.id,
            vulnerability_id=vuln_cve.id,
            title="CVE-2023-44487: HTTP/2 Rapid Reset Denial of Service",
            description="High risk HTTP/2 vulnerability present on nginx 1.22.1 banner.",
            status=FindingStatus.VALIDATED,
            severity=FindingSeverity.HIGH,
            risk_score=75.0,
            confidence_score=95.0,
            remediation="Upgrade nginx to 1.25.3 or higher.",
        )
        session.add(finding)
        await session.flush()

        # 7. Audit Log Entry
        audit = AuditLog(
            action="seed_demo_data",
            entity_type="project",
            entity_id=project.id,
            project_id=project.id,
            actor="seed_script",
            details={"note": "DEMO DATA – NOT A REAL SECURITY ASSESSMENT"},
        )
        session.add(audit)

        await session.commit()
        print("[+] Demo data seeded successfully!")
        print("[+] Note: DEMO DATA – NOT A REAL SECURITY ASSESSMENT")


if __name__ == "__main__":
    asyncio.run(seed_data())
