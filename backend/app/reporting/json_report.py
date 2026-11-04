import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _without_orm_state(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: value for key, value in row.items() if key != "_sa_instance_state"} for row in rows]


class JSONReportGenerator:
    @staticmethod
    def generate_json_report(data: Dict[str, Any], output_path: str) -> str:
        report_payload = {
            "redscope_version": "0.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "disclaimer": "AUTHORIZED SECURITY ASSESSMENT REPORT – PRIVILEGED & CONFIDENTIAL",
            "project": data["project"],
            "scopes": _without_orm_state(data["scopes"]),
            "targets": _without_orm_state(data["targets"]),
            "findings": _without_orm_state(data["findings"]),
            "audit_logs": _without_orm_state(data.get("audit_logs", [])),
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2, default=str)

        return output_path
