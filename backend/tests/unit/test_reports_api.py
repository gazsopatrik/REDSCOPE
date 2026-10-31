from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.reports import download_report
from app.models.report import ReportFormat
from app.schemas.report import ReportRead
from app.services.report_service import ReportService


@pytest.mark.asyncio
async def test_download_report_uses_generated_file_extension(monkeypatch, tmp_path) -> None:
    report_path = tmp_path / "report-id.md"
    report_path.write_text("# Report", encoding="utf-8")
    report = SimpleNamespace(
        file_path=str(report_path),
        title="Security Assessment",
    )

    async def get_report_by_id(_db, _report_id):
        return report

    monkeypatch.setattr(ReportService, "get_report_by_id", staticmethod(get_report_by_id))

    response = await download_report("report-id", db=object())

    assert "Security%20Assessment.md" in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_download_report_rejects_missing_file(monkeypatch, tmp_path) -> None:
    report = SimpleNamespace(
        file_path=str(tmp_path / "missing.json"),
        title="Security Assessment",
    )

    async def get_report_by_id(_db, _report_id):
        return report

    monkeypatch.setattr(ReportService, "get_report_by_id", staticmethod(get_report_by_id))

    with pytest.raises(HTTPException) as error:
        await download_report("report-id", db=object())

    assert error.value.status_code == 404
    assert error.value.detail == "Report file not found"


def test_report_response_does_not_expose_internal_file_path() -> None:
    report = SimpleNamespace(
        id="report-id", project_id="project-id", title="Security Assessment",
        format=ReportFormat.HTML, file_path="/srv/redscope/reports/private.html",
        created_by="system", created_at=datetime.now(timezone.utc),
    )

    payload = ReportRead.model_validate(report).model_dump()

    assert payload["id"] == "report-id"
    assert "file_path" not in payload
