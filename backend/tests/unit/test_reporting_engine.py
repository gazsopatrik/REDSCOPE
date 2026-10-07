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
