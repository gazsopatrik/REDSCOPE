class KEVProvider:
    KNOWN_EXPLOITED_CVES = {
        "CVE-2023-44487",
        "CVE-2011-2523",
        "CVE-2021-44228",  # Log4Shell
        "CVE-2017-0144",  # EternalBlue
    }

    @classmethod
    def is_known_exploited(cls, cve_id: str) -> bool:
        """Returns True if the CVE is present in CISA's Known Exploited Vulnerabilities catalog."""
        return cve_id in cls.KNOWN_EXPLOITED_CVES
