from app.scoring.risk_engine import RiskEngine


def test_calculate_risk_score_critical() -> None:
    res = RiskEngine.calculate_risk_score(
        cvss_score=9.8,
        epss_score=0.95,
        is_kev=True,
        cpe_match_confidence="exact",
        is_public_exposure=True,
        has_public_poc=True,
        is_validated=True,
    )
    assert res.final_score >= 80.0
    assert res.severity_label == "Critical"
    assert res.kev_points == 15.0
    assert "Risk Score" in res.human_explanation


def test_calculate_risk_score_low() -> None:
    res = RiskEngine.calculate_risk_score(
        cvss_score=2.0,
        epss_score=0.01,
        is_kev=False,
        cpe_match_confidence="low",
        is_public_exposure=False,
        has_public_poc=False,
        is_validated=False,
    )
    assert res.final_score < 40.0
    assert res.severity_label in ("Low", "Informational")
