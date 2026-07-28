from app.scoring.confidence import ConfidenceEngine


def test_confidence_score_exact() -> None:
    res = ConfidenceEngine.calculate_confidence_score(
        cpe_match_type="exact",
        has_version_number=True,
        is_safe_validation_passed=True,
    )
    assert res.final_score >= 90.0
    assert len(res.factors) >= 3


def test_confidence_score_unreliable() -> None:
    res = ConfidenceEngine.calculate_confidence_score(
        cpe_match_type="low",
        has_version_number=False,
        is_generic_service_name=True,
        has_proxy_or_load_balancer=True,
    )
    assert res.final_score < 40.0
