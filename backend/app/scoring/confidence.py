from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ConfidenceScoreBreakdown:
    final_score: float
    factors: List[str]
    human_explanation: str


class ConfidenceEngine:
    @classmethod
    def calculate_confidence_score(
        cls,
        cpe_match_type: str = "medium",  # exact, high, medium, low
        has_version_number: bool = True,
        is_generic_service_name: bool = False,
        has_proxy_or_load_balancer: bool = False,
        is_safe_validation_passed: bool = False,
    ) -> ConfidenceScoreBreakdown:
        """
        Calculates an independent confidence score (0 to 100) representing detection accuracy and fidelity.
        """
        base_score = 50.0
        factors: List[str] = []

        # CPE Match Type factor
        if cpe_match_type == "exact":
            base_score += 25.0
            factors.append("+25: Exact CPE identifier match")
        elif cpe_match_type == "high":
            base_score += 15.0
            factors.append("+15: High product match")
        elif cpe_match_type == "low":
            base_score -= 15.0
            factors.append("-15: Low confidence generic match")

        # Version presence
        if has_version_number:
            base_score += 15.0
            factors.append("+15: Explicit service version string present")
        else:
            base_score -= 20.0
            factors.append("-20: Missing explicit version number")

        # Generic service name penalty
        if is_generic_service_name:
            base_score -= 10.0
            factors.append("-10: Generic service port heuristic")

        # Proxy / Load balancer penalty
        if has_proxy_or_load_balancer:
            base_score -= 15.0
            factors.append("-15: Reverse proxy or load balancer detected")

        # Safe validation boost
        if is_safe_validation_passed:
            base_score += 20.0
            factors.append("+20: Confirmed via non-destructive validation check")

        final_score = round(min(max(base_score, 0.0), 100.0), 1)
        explanation = f"Confidence Score {final_score}/100. Factors: {', '.join(factors)}."

        return ConfidenceScoreBreakdown(
            final_score=final_score,
            factors=factors,
            human_explanation=explanation,
        )
