import re
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class NormalizedServiceInfo:
    vendor: str
    product: str
    version: Optional[str]
    cpe_23: str
    confidence: str  # exact, high, medium, low, unknown


class CPEMatcher:
    KNOWN_MAPPINGS = {
        "nginx": ("nginx", "nginx"),
        "apache httpd": ("apache", "http_server"),
        "apache": ("apache", "http_server"),
        "openssh": ("openbsd", "openssh"),
        "vsftpd": ("vsftpd", "vsftpd"),
        "mysql": ("oracle", "mysql"),
        "postgresql": ("postgresql", "postgresql"),
        "microsoft iis": ("microsoft", "iis"),
        "iis": ("microsoft", "iis"),
        "samba": ("samba", "samba"),
    }

    @classmethod
    def normalize_service(
        cls,
        product: Optional[str],
        version: Optional[str],
        service_name: Optional[str],
        cpe_raw: Optional[str] = None,
    ) -> NormalizedServiceInfo:
        """Normalizes raw service banners into CPE 2.3 identifiers with match confidence."""
        # 1. If raw CPE string is already provided by Nmap
        if cpe_raw and cpe_raw.startswith("cpe:/"):
            parts = cpe_raw.split(":")
            if len(parts) >= 5:
                part_type = parts[1]  # /a, /h, /o
                part_code = "a" if "a" in part_type else "h" if "h" in part_type else "o"
                vendor = parts[2]
                prod = parts[3]
                ver = parts[4] if len(parts) > 4 else "*"
                cpe23 = f"cpe:2.3:{part_code}:{vendor}:{prod}:{ver}:*:*:*:*:*:*:*"
                return NormalizedServiceInfo(
                    vendor=vendor,
                    product=prod,
                    version=ver if ver != "*" else version,
                    cpe_23=cpe23,
                    confidence="exact",
                )

        raw_prod = (product or service_name or "unknown").strip().lower()
        clean_version = version.strip() if version else "*"

        # Check rule-based mappings
        for key, (vendor, prod_name) in cls.KNOWN_MAPPINGS.items():
            if key in raw_prod:
                cpe23 = f"cpe:2.3:a:{vendor}:{prod_name}:{clean_version}:*:*:*:*:*:*:*"
                conf = "high" if version else "medium"
                return NormalizedServiceInfo(
                    vendor=vendor,
                    product=prod_name,
                    version=version,
                    cpe_23=cpe23,
                    confidence=conf,
                )

        # Fallback generic normalization
        safe_name = re.sub(r"[^a-z0-9_]", "_", raw_prod)
        cpe23 = f"cpe:2.3:a:generic:{safe_name}:{clean_version}:*:*:*:*:*:*:*"
        return NormalizedServiceInfo(
            vendor="generic",
            product=safe_name,
            version=version,
            cpe_23=cpe23,
            confidence="low" if not version else "medium",
        )
