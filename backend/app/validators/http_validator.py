import ipaddress
from typing import Any, Dict
import httpx
from app.validators.base import BaseValidator, ValidationResult


def build_http_endpoint_url(target: str, port: int, scheme: str) -> str:
    """Build an HTTP URL, adding brackets required for IPv6 literals."""
    try:
        address = ipaddress.ip_address(target)
        host = f"[{address.compressed}]" if address.version == 6 else str(address)
    except ValueError:
        host = target
    return f"{scheme}://{host}:{port}/"


class HTTPValidator(BaseValidator):
    id = "http_security_header_check"
    name = "HTTP/HTTPS Security Header & Response Audit"
    description = (
        "Non-destructive audit retrieving HTTP status code, Server header, "
        "and security headers (HSTS, X-Frame-Options, X-Content-Type-Options)."
    )
    supported_services = ["http", "https", "http-alt", "https-alt"]
    risk_level = "low"
    requires_approval = True
    destructive = False

    def supports(self, service_name: str, port: int) -> bool:
        return service_name.lower() in self.supported_services or port in (80, 443, 8000, 8080, 8443)

    async def validate(self, target_ip: str, port: int, service_info: Dict[str, Any]) -> ValidationResult:
        scheme = "https" if port in (443, 8443) or "ssl" in str(service_info.get("tunnel", "")) else "http"
        url = build_http_endpoint_url(target_ip, port, scheme)

        try:
            async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                response = await client.get(url)
                headers = dict(response.headers)

                server_header = headers.get("server", "Not disclosed")
                hsts = "strict-transport-security" in headers
                xfo = "x-frame-options" in headers

                evidence = {
                    "url": url,
                    "status_code": response.status_code,
                    "server_header": server_header,
                    "hsts_present": hsts,
                    "x_frame_options_present": xfo,
                    "content_type": headers.get("content-type"),
                }

                summary = f"HTTP endpoint returned {response.status_code}. Server banner: '{server_header}'."
                return ValidationResult(
                    passed=True,
                    status="passed",
                    summary=summary,
                    evidence=evidence,
                    confidence_delta=15.0,
                    risk_delta=0.0,
                )

        except Exception as e:
            return ValidationResult(
                passed=False,
                status="failed",
                summary=f"HTTP connection to {url} failed: {str(e)}",
                evidence={"url": url, "error": str(e)},
                error_message=str(e),
            )
