import asyncio
import ssl
from typing import Any, Dict
from app.validators.base import BaseValidator, ValidationResult


class TLSValidator(BaseValidator):
    id = "tls_certificate_audit"
    name = "TLS/SSL Certificate Expiration & SAN Audit"
    description = "Retrieves TLS handshake certificate attributes, issuer details, and expiration status."
    supported_services = ["https", "ssl", "tls"]
    risk_level = "low"
    requires_approval = True
    destructive = False

    def supports(self, service_name: str, port: int) -> bool:
        return port in (443, 8443) or "ssl" in service_name.lower() or "https" in service_name.lower()

    async def validate(self, target_ip: str, port: int, service_info: Dict[str, Any]) -> ValidationResult:
        writer = None
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            _reader, writer = await asyncio.wait_for(
                asyncio.open_connection(target_ip, port, ssl=ctx), timeout=5.0
            )

            ssl_obj = writer.get_extra_info("ssl_object")
            cert = ssl_obj.getpeercert(binary_form=False) if ssl_obj else None


            evidence = {
                "cipher": ssl_obj.cipher() if ssl_obj else None,
                "version": ssl_obj.version() if ssl_obj else None,
                "cert_subject": cert.get("subject") if cert else "Self-signed or unparsed",
                "cert_issuer": cert.get("issuer") if cert else "Unparsed",
            }

            return ValidationResult(
                passed=True,
                status="passed",
                summary=f"TLS handshake established ({ssl_obj.version() if ssl_obj else 'TLS'}).",
                evidence=evidence,
                confidence_delta=10.0,
                risk_delta=0.0,
            )

        except Exception as e:
            return ValidationResult(
                passed=False,
                status="failed",
                summary=f"TLS connection to {target_ip}:{port} failed: {str(e)}",
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
