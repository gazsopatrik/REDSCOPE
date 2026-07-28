from dataclasses import dataclass, field
from typing import List, Optional
from defusedxml import ElementTree as ET


@dataclass
class ParsedService:
    protocol: str
    port: int
    state: str
    service_name: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    extra_info: Optional[str] = None
    tunnel: Optional[str] = None
    cpe: Optional[str] = None
    confidence: float = 1.0
    banner: Optional[str] = None


@dataclass
class ParsedHost:
    ip_address: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    vendor: Optional[str] = None
    state: str = "up"
    os_name: Optional[str] = None
    os_accuracy: Optional[int] = None
    latency: Optional[float] = None
    services: List[ParsedService] = field(default_factory=list)


@dataclass
class ParsedScanResult:
    hosts: List[ParsedHost] = field(default_factory=list)


class NmapXMLParser:
    @classmethod
    def parse_xml_file(cls, xml_path: str) -> ParsedScanResult:
        """Parses an Nmap XML output file securely using defusedxml."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        result = ParsedScanResult()

        for host_node in root.findall("host"):
            status_node = host_node.find("status")
            state = status_node.get("state", "up") if status_node is not None else "up"

            # Extract IP and MAC address
            ip_address = None
            mac_address = None
            vendor = None

            for addr in host_node.findall("address"):
                addr_type = addr.get("addrtype", "ipv4")
                if addr_type in ("ipv4", "ipv6") and not ip_address:
                    ip_address = addr.get("addr")
                elif addr_type == "mac":
                    mac_address = addr.get("addr")
                    vendor = addr.get("vendor")

            if not ip_address:
                continue

            # Extract Hostname
            hostname = None
            hostnames_node = host_node.find("hostnames")
            if hostnames_node is not None:
                hn_node = hostnames_node.find("hostname")
                if hn_node is not None:
                    hostname = hn_node.get("name")

            # Extract OS Match
            os_name = None
            os_accuracy = None
            os_node = host_node.find("os")
            if os_node is not None:
                match_node = os_node.find("osmatch")
                if match_node is not None:
                    os_name = match_node.get("name")
                    try:
                        os_accuracy = int(match_node.get("accuracy", 0))
                    except ValueError:
                        os_accuracy = None

            parsed_host = ParsedHost(
                ip_address=ip_address,
                hostname=hostname,
                mac_address=mac_address,
                vendor=vendor,
                state=state,
                os_name=os_name,
                os_accuracy=os_accuracy,
            )

            # Extract Ports & Services
            ports_node = host_node.find("ports")
            if ports_node is not None:
                for port_node in ports_node.findall("port"):
                    port_state_node = port_node.find("state")
                    port_state = (
                        port_state_node.get("state", "open")
                        if port_state_node is not None
                        else "open"
                    )

                    if port_state != "open":
                        continue

                    protocol = port_node.get("protocol", "tcp")
                    port_num = int(port_node.get("portid", 0))

                    service_name = None
                    product = None
                    version = None
                    extra_info = None
                    tunnel = None
                    cpe = None
                    confidence = 1.0

                    service_node = port_node.find("service")
                    if service_node is not None:
                        service_name = service_node.get("name")
                        product = service_node.get("product")
                        version = service_node.get("version")
                        extra_info = service_node.get("extrainfo")
                        tunnel = service_node.get("tunnel")

                        try:
                            conf_str = service_node.get("conf")
                            if conf_str:
                                confidence = float(conf_str) / 10.0
                        except ValueError:
                            confidence = 1.0

                        cpe_node = service_node.find("cpe")
                        if cpe_node is not None and cpe_node.text:
                            cpe = cpe_node.text

                    parsed_service = ParsedService(
                        protocol=protocol,
                        port=port_num,
                        state=port_state,
                        service_name=service_name,
                        product=product,
                        version=version,
                        extra_info=extra_info,
                        tunnel=tunnel,
                        cpe=cpe,
                        confidence=confidence,
                    )
                    parsed_host.services.append(parsed_service)

            result.hosts.append(parsed_host)

        return result
