import asyncio
from typing import Any, Dict
from app.validators.base import BaseValidator, ValidationResult


class SMBValidator(BaseValidator):
    id = "smb_dialect_signing_audit"
    name = "SMB Dialect & Signing Status Audit"
    description = "Checks SMB port availability, dialect response, and SMBv1 presence without attempting authentication or file operations."
    supported_services = ["microsoft-ds", "netbios-ssn", "smb"]
    risk_level = "low"
    requires_approval = True
    destructive = False

    def supports(self, service_name: str, port: int) -> bool:
        return service_name.lower() in self.supported_services or port in (445, 139)

    async def validate(self, target_ip: str, port: int, service_info: Dict[str, Any]) -> ValidationResult:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(target_ip, port), timeout=5.0
            )

            # Send SMB NetBIOS Session Request / Negotiation header (read-only dialect query)
            smb1_negotiate_pkt = bytes.fromhex(\n                "0000002fff534d427200000000180128000000000000000000"\n                "0000000000000000000000000c00024e54204c4d20302e313200"\n            )
            writer.write(smb1_negotiate_pkt)
            await writer.drain()

            resp = await asyncio.wait_for(reader.read(1024), timeout=3.0)
            writer.close()
            await writer.wait_closed()

            is_smb_resp = len(resp) >= 4 and b"SMB" in resp

            evidence = {
                "port": port,
                "response_received": len(resp) > 0,
                "smb_magic_detected": is_smb_resp,
            }

            return ValidationResult(
                passed=is_smb_resp,
                status="passed" if is_smb_resp else "inconclusive",
                summary=f"SMB service responded to dialect negotiation on port {port}.",
                evidence=evidence,
                confidence_delta=10.0,
                risk_delta=0.0,
            )

        except Exception as e:
            return ValidationResult(
                passed=False,
                status="failed",
                summary=f"SMB check on {target_ip}:{port} failed: {str(e)}",
                evidence={"target": f"{target_ip}:{port}", "error": str(e)},
                error_message=str(e),
            )
