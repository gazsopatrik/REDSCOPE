import pytest
from pydantic import ValidationError

from app.schemas.report import ReportCreate


@pytest.mark.parametrize("title", ["", " ", "\t\n", "\u00a0"])
def test_report_rejects_blank_title(title: str) -> None:
    with pytest.raises(ValidationError):
        ReportCreate(title=title)


def test_report_strips_outer_whitespace_preserving_inner_spaces() -> None:
    assert ReportCreate(title="  Quarterly  Audit\n").title == "Quarterly  Audit"


def test_report_checks_length_after_trimming() -> None:
    assert ReportCreate(title=" " + "x" * 255 + " ").title == "x" * 255
    with pytest.raises(ValidationError):
        ReportCreate(title="x" * 256)


def test_report_keeps_default_title() -> None:
    assert ReportCreate().title == "Security Assessment Executive Report"
