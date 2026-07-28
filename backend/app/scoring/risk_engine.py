from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RiskScoreBreakdown:
    final_score: float
    severity_label: str  # Critical, High, Medium, Low, Informational
    cvss_points: float
    epss_points: float
    kev_points: float
    confidence_points: float
    exposure_points: float
    exploit_maturity_points: float
    validation_points: float
    human_explanation: str


class RiskEngine:
    @classmethod
    def calculate_risk_score(
        cls,
        cvss_score: Optional[float] = None,
        epss_score: Optional[float] = None,
        is_kev: bool = False,
        cpe_match_confidence: str = "medium",  # exact, high, medium, low
        is_public_exposure: bool = True,
        has_public_poc: bool = False,
        is_validated: bool = False,
    ) -> RiskScoreBreakdown:
        """
        Calculates multi-factor risk score (0 to 100) based on weighted formula:
          • CVSS Component (max 25 pts)
          • EPSS Component (max 20 pts)
          • CISA KEV Status (max 15 pts)
          • Match Confidence (max 15 pts)
          • Exposure Level (max 10 pts)
          • Exploit Maturity (max 5 pts)
          • Validation Evidence (max 10 pts)
        """
        # 1. CVSS Component (0-10 scale mapped to 25 max pts)
        cvss_val = cvss_score if cvss_score is not None else 5.0
        cvss_pts = (cvss_val / 10.0) * 25.0

        # 2. EPSS Component (0.0-1.0 scale mapped to 20 max pts)
        epss_val = epss_score if epss_score is not None else 0.05
        epss_pts = min(epss_val * 20.0, 20.0)

        # 3. KEV Status (15 pts if actively exploited in the wild)
        kev_pts = 15.0 if is_kev else 0.0

        # 4. Match Confidence Component (exact=15, high=12, medium=8, low=3)
        conf_map = {"exact": 15.0, "high": 12.0, "medium": 8.0, "low": 3.0}
        conf_pts = conf_map.get(cpe_match_confidence.lower(), 8.0)

        # 5. Exposure Component (10 pts if publicly accessible)
        exp_pts = 10.0 if is_public_exposure else 5.0

        # 6. Exploit Maturity (5 pts if public PoC code exists)
        exploit_pts = 5.0 if has_public_poc else 0.0

        # 7. Validation Evidence (10 pts if confirmed via safe non-destructive validator)
        valid_pts = 10.0 if is_validated else 0.0

        total_raw = cvss_pts + epss_pts + kev_pts + conf_pts + exp_pts + exploit_pts + valid_pts
        final_score = round(min(max(total_raw, 0.0), 100.0), 1)

        # Map score to severity priority category
        if final_score >= 80.0:
            severity = "Critical"
        elif final_score >= 60.0:
            severity = "High"
        elif final_score >= 40.0:
            severity = "Medium"
        elif final_score >= 20.0:
            severity = "Low"
        else:
            severity = "Informational"

        explanation = (
            f"Risk Score {final_score}/100 [{severity}]. "
            f"CVSS contribution: {cvss_pts:.1f}/25 (base CVSS {cvss_val}); "
            f"EPSS probability: {epss_pts:.1f}/20 (score {epss_val}); "
            f"CISA KEV: {kev_pts:.1f}/15; "
            f"Match Confidence: {conf_pts:.1f}/15 ({cpe_match_confidence}); "
            f"Exposure: {exp_pts:.1f}/10; "
            f"Validation Evidence: {valid_pts:.1f}/10."
        )

        return RiskScoreBreakdown(
            final_score=final_score,
            severity_label=severity,
            cvss_points=round(cvss_pts, 1),
            epss_points=round(epss_pts, 1),
            kev_points=round(kev_pts, 1),
            confidence_points=round(conf_pts, 1),
            exposure_points=round(exp_pts, 1),
            exploit_maturity_points=round(exploit_pts, 1),
            validation_points=round(valid_pts, 1),
            human_explanation=explanation,
        )
