from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from jinja2 import Template

HTML_TEMPLATE_STR = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RedScope Security Report - {{ project.name }}</title>
    <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; background-color: #0b0f19; color: #f9fafb; margin: 0; padding: 2rem; }
        .container { max-width: 1000px; margin: 0 auto; background-color: #111827; padding: 2rem; border-radius: 12px; border: 1px solid #1f2937; }
        h1 { color: #ef4444; margin-top: 0; border-bottom: 2px solid #1f2937; padding-bottom: 1rem; }
        .meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .meta-card { background-color: #1f2937; padding: 1rem; border-radius: 8px; font-size: 0.9rem; }
        .meta-label { color: #9ca3af; font-size: 0.75rem; text-transform: uppercase; }
        .meta-value { font-weight: bold; margin-top: 0.25rem; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th, td { padding: 0.75rem 1rem; border-bottom: 1px solid #1f2937; text-align: left; }
        th { color: #9ca3af; font-size: 0.85rem; }
        .badge { padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
        .badge-critical { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
        .badge-high { background: rgba(249, 115, 22, 0.2); color: #f97316; border: 1px solid #f97316; }
        .badge-medium { background: rgba(234, 179, 8, 0.2); color: #eab308; border: 1px solid #eab308; }
        .disclaimer { font-size: 0.8rem; color: #6b7280; margin-top: 3rem; text-align: center; border-top: 1px solid #1f2937; padding-top: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ RedScope Security Assessment Report</h1>
        
        <div class="meta-grid">
            <div class="meta-card">
                <div class="meta-label">Project Name</div>
                <div class="meta-value">{{ project.name }}</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">Client</div>
                <div class="meta-value">{{ project.client_name or 'N/A' }}</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">Authorization Ref</div>
                <div class="meta-value">{{ project.authorization_reference or 'N/A' }}</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">Generated At</div>
                <div class="meta-value">{{ generated_at }}</div>
            </div>
        </div>

        <h2>Executive Summary</h2>
        <p>Total Scoped Targets: <strong>{{ targets | length }}</strong> | Total Findings Discovered: <strong>{{ findings | length }}</strong></p>

        <h2>Discovered Findings</h2>
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Risk Score</th>
                    <th>Finding Title</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for f in findings %}
                <tr>
                    <td><span class="badge badge-{{ f.severity }}">{{ f.severity }}</span></td>
                    <td><strong>{{ f.risk_score }}</strong>/100</td>
                    <td>{{ f.title }}</td>
                    <td>{{ f.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="disclaimer">
            CONFIDENTIAL SECURITY AUDIT REPORT – AUTHORIZED ASSESSMENT ONLY
        </div>
    </div>
</body>
</html>
"""


class HTMLReportGenerator:
    @staticmethod
    def generate_html_report(data: Dict[str, Any], output_path: str) -> str:
        template = Template(HTML_TEMPLATE_STR)
        rendered_html = template.render(
            project=data["project"],
            scopes=data["scopes"],
            targets=data["targets"],
            findings=data["findings"],
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        return output_path
