from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class MarkdownReportGenerator:
    @staticmethod
    def generate_markdown_report(data: Dict[str, Any], output_path: str) -> str:
        proj = data["project"]
        findings = data["findings"]
        targets = data["targets"]

        md_content = f"""# RedScope Security Assessment Report: {proj['name']}

**Client**: {proj.get('client_name') or 'N/A'}  
**Status**: {proj['status']}  
**Generated At**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Authorization Ref**: {proj.get('authorization_reference') or 'N/A'}  

---

> [!IMPORTANT]
> **PRIVILEGED & CONFIDENTIAL**  
> This security assessment report was generated exclusively for authorized security verification.

---

## 1. Executive Summary

- **Total Targets Assessed**: {len(targets)}
- **Total Findings**: {len(findings)}
- **Critical Risk Findings**: {sum(1 for f in findings if f.get('severity') == 'critical')}
- **High Risk Findings**: {sum(1 for f in findings if f.get('severity') == 'high')}

---

## 2. Findings Detail

"""
        for idx, f in enumerate(findings, 1):
            md_content += f"""### Finding #{idx}: {f['title']}

- **Severity**: {f['severity'].upper()}
- **Risk Score**: {f['risk_score']}/100
- **Confidence**: {f['confidence_score']}/100
- **Status**: {f['status']}
- **Description**: {f.get('description') or 'N/A'}
- **Remediation**: {f.get('remediation') or 'N/A'}

---
"""

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return output_path
