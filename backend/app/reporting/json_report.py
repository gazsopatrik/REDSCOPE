import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class JSONReportGenerator:
    @staticmethod
    def generate_json_report(data: Dict[str, Any], output_path: str) -> str:
        report_payload = {
            "redscope_version": "0.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "disclaimer": "AUTHORIZED SECURITY ASSESSMENT REPORT – PRIVILEGED & CONFIDENTIAL",
            "project": data["project"],
            "scopes": data["scopes"],
            "targets": data["targets"],
            "findings": data["findings"],
            "audit_logs": data.get("audit_logs", []),
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2, default=str)

        return output_path
