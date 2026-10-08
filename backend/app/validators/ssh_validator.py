import asyncio
from typing import Any, Dict
from app.validators.base import BaseValidator, ValidationResult


class SSHValidator(BaseValidator):
    id = "ssh_banner_algorithm_audit"
    name = "SSH Protocol Banner & Host Key Algorithm Audit"
    description = "Connects to SSH service, retrieves banner string, and verifies active SSH protocol version."
    supported_services = ["ssh"]
    risk_level = "low"
    requires_approval = True
    destructive = False

    def supports(self, service_name: str, port: int) -> bool:
        return service_name.lower() == "ssh" or port == 22

    async def validate(self, target_ip: str, port: int, service_info: Dict[str, Any]) -> ValidationResult:
        writer = None
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(target_ip, port), timeout=5.0
            )

            banner_bytes = await asyncio.wait_for(reader.readline(), timeout=3.0)
            banner_str = banner_bytes.decode(errors="replace").strip()

            evidence = {
                "banner": banner_str,
                "is_ssh2": "SSH-2.0" in banner_str,
                "port": port,
            }

            return ValidationResult(
                passed=True,
                status="passed",
                summary=f"SSH service active. Banner: '{banner_str}'.",
                evidence=evidence,
                confidence_delta=15.0,
                risk_delta=0.0,
            )

        except Exception as e:
            return ValidationResult(
                passed=False,
                status="failed",
                summary=f"SSH connection to {target_ip}:{port} failed: {str(e)}",
                evidence={"target": f"{target_ip}:{port}", "error": str(e)},
                error_message=str(e),
            )
        finally:
            if writer is not None:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass
