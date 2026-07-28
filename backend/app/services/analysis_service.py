from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.intelligence.cpe_matcher import CPEMatcher
from app.intelligence.cve_provider import CVEProvider
from app.intelligence.epss_provider import EPSSProvider
from app.intelligence.kev_provider import KEVProvider
from app.models.finding import Finding, FindingSeverity, FindingStatus
from app.models.service import Service
from app.models.vulnerability import Vulnerability


class AnalysisService:
    @staticmethod
    async def analyze_service_and_generate_findings(
        db: AsyncSession, service: Service
    ) -> List[Finding]:
        """
        Normalizes a service banner, queries vulnerability providers, and generates finding candidates.
        Finding candidates initial status is SUSPECTED or CANDIDATE.
        """
        norm = CPEMatcher.normalize_service(
            product=service.product,
            version=service.version,
            service_name=service.service_name,
            cpe_raw=service.cpe,
        )

        # Update service with normalized CPE
        service.cpe = norm.cpe_23

        cves = CVEProvider.lookup_cves(
            vendor=norm.vendor, product=norm.product, version=norm.version
        )

        generated_findings: List[Finding] = []

        if not cves:
            await db.commit()
            return []

        for cve_data in cves:
            # Check or create Vulnerability entity in DB
            vuln_res = await db.execute(
                select(Vulnerability).where(Vulnerability.cve_id == cve_data.cve_id)
            )
            vuln = vuln_res.scalar_one_or_none()

            if not vuln:
                vuln = Vulnerability(
                    cve_id=cve_data.cve_id,
                    title=cve_data.title,
                    description=cve_data.description,
                    cvss_score=cve_data.cvss_score,
                    cvss_vector=cve_data.cvss_vector,
                    severity=cve_data.severity,
                    cwe_ids=cve_data.cwe_ids,
                    references=cve_data.references,
                    known_exploited=cve_data.known_exploited,
                    epss_score=cve_data.epss_score,
                    epss_percentile=cve_data.epss_percentile,
                )
                db.add(vuln)
                await db.flush()

            # Check if finding already exists for this service + vulnerability
            finding_res = await db.execute(
                select(Finding).where(
                    Finding.service_id == service.id, Finding.vulnerability_id == vuln.id
                )
            )
            existing_finding = finding_res.scalar_one_or_none()
            if existing_finding:
                continue

            sev_map = {
                "critical": FindingSeverity.CRITICAL,
                "high": FindingSeverity.HIGH,
                "medium": FindingSeverity.MEDIUM,
                "low": FindingSeverity.LOW,
            }
            finding_sev = sev_map.get(cve_data.severity.lower(), FindingSeverity.MEDIUM)

            finding = Finding(
                service_id=service.id,
                vulnerability_id=vuln.id,
                title=f"{cve_data.cve_id}: {cve_data.title}",
                description=cve_data.description,
                status=FindingStatus.CANDIDATE,
                severity=finding_sev,
                risk_score=float((cve_data.cvss_score or 5.0) * 10),
                confidence_score=90.0 if norm.confidence == "exact" else 70.0,
                match_method=f"CPE match ({norm.confidence})",
                evidence={
                    "service_name": service.service_name,
                    "product": service.product,
                    "version": service.version,
                    "cpe": norm.cpe_23,
                    "cve_id": cve_data.cve_id,
                    "cvss_score": cve_data.cvss_score,
                },
                remediation=f"Upgrade {norm.product} to the latest patched version.",
            )
            db.add(finding)
            generated_findings.append(finding)

        await db.commit()
        return generated_findings
