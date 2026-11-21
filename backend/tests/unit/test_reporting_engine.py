import json
from enum import Enum
import tempfile
from pathlib import Path
from app.reporting.html_report import HTMLReportGenerator
from app.reporting.json_report import JSONReportGenerator
from app.reporting.markdown_report import MarkdownReportGenerator


def get_mock_report_data() -> dict:
    return {
        "project": {
            "id": "p-100",
            "name": "Acme Security Audit",
            "client_name": "Acme Corp",
            "status": "active",
            "authorization_reference": "AUTH-123",
        },
        "scopes": [{"value": "192.168.1.0/24"}],
        "targets": [{"target_value": "192.168.1.10"}],
        "findings": [
            {
                "title": "CVE-2023-44487 HTTP/2 Rapid Reset",
                "severity": "high",
                "risk_score": 75.0,
                "confidence_score": 90.0,
                "status": "candidate",
                "description": "HTTP/2 DoS vulnerability",
                "remediation": "Update nginx",
            }
        ],
    }


def test_html_report_generator() -> None:
    data = get_mock_report_data()
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        temp_path = f.name

    try:
        out = HTMLReportGenerator.generate_html_report(data, temp_path)
        assert Path(out).exists()
        content = Path(out).read_text(encoding="utf-8")
        assert "Acme Security Audit" in content
        assert "CVE-2023-44487" in content
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_html_report_escapes_untrusted_values() -> None:
    data = get_mock_report_data()
    data["project"]["name"] = "<script>alert('project')</script>"
    data["findings"][0]["title"] = "<img src=x onerror=alert('finding')>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        temp_path = f.name

    try:
        HTMLReportGenerator.generate_html_report(data, temp_path)
        content = Path(temp_path).read_text(encoding="utf-8")
        assert "<script>" not in content
        assert "<img src=x" not in content
        assert "&lt;script&gt;" in content
        assert "&lt;img src=x" in content
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_markdown_report_generator() -> None:
    data = get_mock_report_data()
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        temp_path = f.name

    try:
        out = MarkdownReportGenerator.generate_markdown_report(data, temp_path)
        assert Path(out).exists()
        content = Path(out).read_text(encoding="utf-8")
        assert "RedScope Security Assessment Report" in content
        assert "CVE-2023-44487" in content
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_markdown_report_escapes_raw_html() -> None:
    data = get_mock_report_data()
    data["project"]["name"] = "<script>alert('project')</script>"
    data["findings"][0]["description"] = "<img src=x onerror=alert('finding')>"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        temp_path = f.name

    try:
        MarkdownReportGenerator.generate_markdown_report(data, temp_path)
        content = Path(temp_path).read_text(encoding="utf-8")
        assert "<script>" not in content
        assert "<img src=x" not in content
        assert "&lt;script&gt;" in content
        assert "&lt;img src=x" in content
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_json_report_generator() -> None:
    data = get_mock_report_data()
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        out = JSONReportGenerator.generate_json_report(data, temp_path)
        assert Path(out).exists()
        content = Path(out).read_text(encoding="utf-8")
        assert "redscope_version" in content
        assert "Acme Security Audit" in content
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_json_report_omits_sqlalchemy_state() -> None:
    data = get_mock_report_data()
    for collection in ("scopes", "targets", "findings"):
        data[collection][0]["_sa_instance_state"] = object()

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        JSONReportGenerator.generate_json_report(data, temp_path)
        payload = json.loads(Path(temp_path).read_text(encoding="utf-8"))
        assert payload["scopes"][0]["value"] == "192.168.1.0/24"
        assert payload["targets"][0]["target_value"] == "192.168.1.10"
        assert payload["findings"][0]["title"] == "CVE-2023-44487 HTTP/2 Rapid Reset"
        assert "_sa_instance_state" not in Path(temp_path).read_text(encoding="utf-8")
    finally:
        Path(temp_path).unlink(missing_ok=True)


class Severity(str, Enum):
    HIGH = "high"


class Status(str, Enum):
    CANDIDATE = "candidate"


def test_report_generators_render_enum_values(tmp_path) -> None:
    data = get_mock_report_data()
    data["findings"][0]["severity"] = Severity.HIGH
    data["findings"][0]["status"] = Status.CANDIDATE
    html_path = tmp_path / "report.html"
    md_path = tmp_path / "report.md"
    HTMLReportGenerator.generate_html_report(data, str(html_path))
    MarkdownReportGenerator.generate_markdown_report(data, str(md_path))
    html = html_path.read_text(encoding="utf-8")
    markdown = md_path.read_text(encoding="utf-8")
    assert "badge-high" in html
    assert "Severity.HIGH" not in html + markdown
    assert "Status.CANDIDATE" not in html + markdown
    assert "Critical Risk Findings**: 0" in markdown
    assert "High Risk Findings**: 1" in markdown
