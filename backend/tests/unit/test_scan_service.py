from types import SimpleNamespace

import pytest
from app.models.scan import ScanProfile, ScanStatus
from app.scanners.nmap_parser import NmapXMLParser
from app.scanners.nmap_runner import NmapRunner
from app.services.audit_service import AuditService
from app.services.scan_service import ScanService


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("create_empty_xml", "stderr", "exit_code"),
    [(False, "Scan process timed out", -1), (True, "", 0)],
)
async def test_scan_without_xml_fails_with_runner_diagnostic(
    monkeypatch, tmp_path, create_empty_xml, stderr, exit_code
) -> None:
    xml_path = tmp_path / "scan.xml"
    if create_empty_xml:
        xml_path.write_text("", encoding="utf-8")

    scan = SimpleNamespace(id="scan-1", status=ScanStatus.RUNNING, error_message=None)
    audit_events = []

    class FakeSession:
        def __init__(self) -> None:
            self.commits = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def commit(self) -> None:
            self.commits += 1

    db = FakeSession()

    async def run_scan(**_kwargs):
        return exit_code, str(xml_path), "", stderr

    async def get_scan(_db, _scan_id):
        return scan

    async def log_event(**kwargs):
        audit_events.append(kwargs)

    def parse_xml(_path):
        raise AssertionError("XML parser must not run without XML output")

    monkeypatch.setattr(NmapRunner, "run_scan_async", run_scan)
    monkeypatch.setattr(ScanService, "get_scan_by_id", get_scan)
    monkeypatch.setattr(AuditService, "log_event", log_event)
    monkeypatch.setattr(NmapXMLParser, "parse_xml_file", parse_xml)
    monkeypatch.setattr("app.services.scan_service.AsyncSessionLocal", lambda: db)

    await ScanService._execute_scan_background(
        scan_id="scan-1",
        target_id="target-1",
        project_id="project-1",
        target_value="192.0.2.1",
        profile=ScanProfile.QUICK_DISCOVERY,
    )

    assert scan.status == ScanStatus.FAILED
    assert scan.exit_code == exit_code
    assert scan.finished_at is not None
    assert scan.error_message == (stderr or "Nmap produced no XML output (exit code 0).")
    assert db.commits == 1
    assert audit_events[0]["action"] == "scan_failed"
    assert audit_events[0]["details"]["error"] == scan.error_message


@pytest.mark.asyncio
async def test_runner_exception_records_scan_failure(monkeypatch) -> None:
    scan = SimpleNamespace(id="scan-1", status=ScanStatus.RUNNING, error_message=None)
    audit_events = []

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def commit(self) -> None:
            pass

    async def run_scan(**_kwargs):
        raise RuntimeError("Nmap unavailable")

    async def get_scan(_db, _scan_id):
        return scan

    async def log_event(**kwargs):
        audit_events.append(kwargs)

    monkeypatch.setattr(NmapRunner, "run_scan_async", run_scan)
    monkeypatch.setattr(ScanService, "get_scan_by_id", get_scan)
    monkeypatch.setattr(AuditService, "log_event", log_event)
    monkeypatch.setattr("app.services.scan_service.AsyncSessionLocal", FakeSession)

    await ScanService._execute_scan_background(
        scan_id="scan-1",
        target_id="target-1",
        project_id="project-1",
        target_value="192.0.2.1",
        profile=ScanProfile.QUICK_DISCOVERY,
    )

    assert scan.status == ScanStatus.FAILED
    assert scan.finished_at is not None
    assert scan.error_message == "Subprocess error: Nmap unavailable"
    assert len(audit_events) == 1
    assert audit_events[0]["action"] == "scan_failed"
    assert audit_events[0]["details"]["error"] == scan.error_message
