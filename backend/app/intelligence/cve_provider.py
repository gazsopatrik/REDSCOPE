from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CVEIntelligenceData:
    cve_id: str
    title: str
    description: str
    cvss_score: float
    cvss_vector: str
    severity: str
    cwe_ids: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    known_exploited: bool = False
    epss_score: float = 0.0
    epss_percentile: float = 0.0


class CVEProvider:
    # Curated offline database / local cache of critical vulnerabilities for popular products
    KNOWN_CVE_DATABASE: Dict[Tuple[str, str, str], List[CVEIntelligenceData]] = {
        ("nginx", "nginx", "1.22.1"): [
            CVEIntelligenceData(
                cve_id="CVE-2023-44487",
                title="HTTP/2 Rapid Reset Denial of Service",
                description="The HTTP/2 protocol allows a high volume of requests with RST_STREAM frames, resulting in significant CPU utilization.",
                cvss_score=7.5,
                cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                severity="high",
                cwe_ids=["CWE-400"],
                references=["https://nvd.nist.gov/vuln/detail/CVE-2023-44487"],
                known_exploited=True,
                epss_score=0.85,
                epss_percentile=0.92,
            )
        ],
        ("vsftpd", "vsftpd", "2.3.4"): [
            CVEIntelligenceData(
                cve_id="CVE-2011-2523",
                title="vsftpd 2.3.4 Backdoor Execution",
                description="vsftpd version 2.3.4 contains a backdoor in the smile face emoticon string that opens a listening shell on port 6200.",
                cvss_score=9.8,
                cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                severity="critical",
                cwe_ids=["CWE-94"],
                references=["https://nvd.nist.gov/vuln/detail/CVE-2011-2523"],
                known_exploited=True,
                epss_score=0.97,
                epss_percentile=0.99,
            )
        ],
        ("openbsd", "openssh", "7.2p1"): [
            CVEIntelligenceData(
                cve_id="CVE-2016-10009",
                title="OpenSSH PKCS#11 Provider Arbitrary Code Execution",
                description="Untrusted library loading in OpenSSH ssh-agent allows remote code execution when agent forwarding is active.",
                cvss_score=7.8,
                cvss_vector="CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H",
                severity="high",
                cwe_ids=["CWE-426"],
                references=["https://nvd.nist.gov/vuln/detail/CVE-2016-10009"],
                known_exploited=False,
                epss_score=0.12,
                epss_percentile=0.45,
            )
        ],
    }

    @classmethod
    def lookup_cves(cls, vendor: str, product: str, version: Optional[str]) -> List[CVEIntelligenceData]:
        """Look up known CVEs matching product and version."""
        if not version:
            return []

        # Try exact key lookup
        for (v_key, p_key, ver_key), cves in cls.KNOWN_CVE_DATABASE.items():
            if v_key.lower() == vendor.lower() and p_key.lower() == product.lower() and ver_key == version:
                return cves

        # Try product & version match fallback
        for (v_key, p_key, ver_key), cves in cls.KNOWN_CVE_DATABASE.items():
            if p_key.lower() in product.lower() and ver_key == version:
                return cves

        return []
