import ipaddress
import socket
from itertools import islice
from dataclasses import dataclass
from typing import List, Tuple
from app.models.scope import Scope, ScopeType
from app.models.target import ScopeStatus


@dataclass
class ScopeValidationDecision:
    status: ScopeStatus
    is_allowed: bool
    message: str
    resolved_ips: List[str]


class ScopeValidator:
    @staticmethod
    def resolve_target(target_value: str) -> Tuple[bool, List[str], str]:
        """Resolves target string to IP addresses. Supports single IP, CIDR, and hostnames."""
        target_str = target_value.strip()

        # Try single IP address
        try:
            ip_obj = ipaddress.ip_address(target_str)
            return True, [str(ip_obj)], "Single IP address resolved successfully"
        except ValueError:
            pass

        # Try CIDR network
        try:
            net_obj = ipaddress.ip_network(target_str, strict=False)
            # Never approve a CIDR after validating only a subset of its hosts.
            # Bound enumeration so large IPv4/IPv6 networks cannot exhaust memory.
            hosts = [str(ip) for ip in islice(net_obj.hosts(), 257)]
            if len(hosts) > 256:
                return False, [], f"CIDR network {net_obj} exceeds the 256-host validation limit"
            return True, hosts, f"CIDR network {net_obj} validated"
        except ValueError:
            pass

        # Try Hostname / Domain DNS resolution
        try:
            _, _, ip_list = socket.gethostbyname_ex(target_str)
            if not ip_list:
                return False, [], f"DNS resolution yielded no IP addresses for {target_str}"
            return True, ip_list, f"Hostname resolved to {len(ip_list)} IP address(es)"
        except socket.gaierror as e:
            return False, [], f"DNS resolution failed for {target_str}: {str(e)}"
        except Exception as e:
            return False, [], f"Resolution error for {target_str}: {str(e)}"

    @classmethod
    def evaluate_target_against_scopes(
        cls, target_value: str, scopes: List[Scope]
    ) -> ScopeValidationDecision:
        """
        Evaluates a target against active project inclusion and exclusion scopes.
        Strict Safety Rule: If ANY resolved IP is in an exclusion scope or NOT covered by an inclusion scope,
        the decision is DENIED.
        """
        active_scopes = [s for s in scopes if s.enabled]
        if not active_scopes:
            return ScopeValidationDecision(
                status=ScopeStatus.DENIED,
                is_allowed=False,
                message="Target DENIED: Project has no active scope rules defined.",
                resolved_ips=[],
            )

        # Separate inclusion and exclusion scopes
        inclusions = [s for s in active_scopes if not s.is_exclusion]
        exclusions = [s for s in active_scopes if s.is_exclusion]

        if not inclusions:
            return ScopeValidationDecision(
                status=ScopeStatus.DENIED,
                is_allowed=False,
                message="Target DENIED: No active inclusion scopes configured.",
                resolved_ips=[],
            )

        resolved_ok, resolved_ips, res_msg = cls.resolve_target(target_value)
        if not resolved_ok or not resolved_ips:
            return ScopeValidationDecision(
                status=ScopeStatus.RESOLUTION_FAILED,
                is_allowed=False,
                message=f"Target DENIED: Resolution failed – {res_msg}",
                resolved_ips=[],
            )

        # Check each resolved IP address against exclusions first
        for ip_str in resolved_ips:
            ip_obj = ipaddress.ip_address(ip_str)
            for ex in exclusions:
                if cls._ip_matches_scope(ip_obj, ex):
                    return ScopeValidationDecision(
                        status=ScopeStatus.DENIED,
                        is_allowed=False,
                        message=f"Target DENIED: Resolved IP {ip_str} matches explicit exclusion rule '{ex.value}'.",
                        resolved_ips=resolved_ips,
                    )

        # Check each resolved IP address against inclusions
        for ip_str in resolved_ips:
            ip_obj = ipaddress.ip_address(ip_str)
            covered = False
            for inc in inclusions:
                if cls._ip_matches_scope(ip_obj, inc):
                    covered = True
                    break
            if not covered:
                return ScopeValidationDecision(
                    status=ScopeStatus.DENIED,
                    is_allowed=False,
                    message=f"Target DENIED: Resolved IP {ip_str} is outside all permitted inclusion scopes.",
                    resolved_ips=resolved_ips,
                )

        # If all resolved IPs pass inclusion and exclusion checks:
        return ScopeValidationDecision(
            status=ScopeStatus.ALLOWED,
            is_allowed=True,
            message=f"Target ALLOWED: All resolved IP(s) [{', '.join(resolved_ips)}] are within authorized scope.",
            resolved_ips=resolved_ips,
        )

    @staticmethod
    def _ip_matches_scope(ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address, scope: Scope) -> bool:
        """Checks if a given IP address object matches a single scope definition."""
        val = scope.value.strip()

        if scope.scope_type == ScopeType.SINGLE_IP:
            try:
                scope_ip = ipaddress.ip_address(val)
                return ip_obj == scope_ip
            except ValueError:
                return False

        elif scope.scope_type == ScopeType.CIDR:
            try:
                net = ipaddress.ip_network(val, strict=False)
                return ip_obj in net
            except ValueError:
                return False

        elif scope.scope_type in (ScopeType.HOSTNAME, ScopeType.DOMAIN):
            # Resolve scope hostname to compare IPs
            try:
                _, _, scope_ips = socket.gethostbyname_ex(val)
                return str(ip_obj) in scope_ips
            except Exception:
                return False

        return False
