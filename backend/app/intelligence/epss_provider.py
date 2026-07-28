from typing import Tuple


class EPSSProvider:
    @staticmethod
    def get_epss_score(cve_id: str) -> Tuple[float, float]:
        """Returns (epss_score, epss_percentile) for a given CVE ID."""
        # Simulated lookup map for known CVEs; defaults to low baseline
        known_epss = {
            "CVE-2023-44487": (0.85, 0.92),
            "CVE-2011-2523": (0.97, 0.99),
            "CVE-2016-10009": (0.12, 0.45),
        }
        return known_epss.get(cve_id, (0.01, 0.10))
