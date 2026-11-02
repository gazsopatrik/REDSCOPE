from datetime import datetime, timezone

from app.models.scan import ScanProfile, ScanStatus
from app.schemas.scan import ScanRead


def test_scan_response_does_not_expose_internal_xml_path() -> None:
    scan = ScanRead.model_validate({
        "id": "scan-id",
        "project_id": "project-id",
        "target_id": "target-id",
        "profile": ScanProfile.STANDARD_SERVICE,
        "status": ScanStatus.COMPLETED,
        "created_by": "system",
        "created_at": datetime.now(timezone.utc),
        "xml_output_path": "/srv/redscope/scans/private.xml",
    })

    assert scan.id == "scan-id"
    assert "xml_output_path" not in scan.model_dump()
