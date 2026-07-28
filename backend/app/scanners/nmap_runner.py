import asyncio
import logging
import uuid
from pathlib import Path
from typing import Tuple
from app.config import settings
from app.models.scan import ScanProfile
from app.scanners.scan_profiles import ScanProfileBuilder

logger = logging.getLogger(__name__)

SIMULATED_NMAP_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<nmaprun scanner="nmap" args="nmap -sV {target_value}" version="7.94">
<host>
    <status state="up" reason="echo-reply"/>
    <address addr="{target_value}" addrtype="ipv4"/>
    <hostnames>
        <hostname name="target.local" type="user"/>
    </hostnames>
    <ports>
        <port protocol="tcp" portid="80">
            <state state="open" reason="syn-ack"/>
            <service name="http" product="nginx" version="1.22.1" method="probed" conf="10">
                <cpe>cpe:/a:nginx:nginx:1.22.1</cpe>
            </service>
        </port>
        <port protocol="tcp" portid="22">
            <state state="open" reason="syn-ack"/>
            <service name="ssh" product="OpenSSH" version="7.2p1" method="probed" conf="10">
                <cpe>cpe:/a:openbsd:openssh:7.2p1</cpe>
            </service>
        </port>
    </ports>
    <os>
        <osmatch name="Linux 5.4 - 5.15" accuracy="95"/>
    </os>
</host>
</nmaprun>
"""


class NmapRunner:
    @classmethod
    async def run_scan_async(
        cls,
        target_value: str,
        profile: ScanProfile,
        custom_ports: str | None = None,
        timeout_seconds: int = 1800,
    ) -> Tuple[int, str, str, str]:
        """
        Executes an Nmap scan safely using asyncio.create_subprocess_exec (shell=False).
        Returns tuple: (exit_code, xml_output_path, stdout_str, stderr_str)
        """
        scan_id = str(uuid.uuid4())
        settings.SCANS_DIR.mkdir(parents=True, exist_ok=True)
        xml_output_path = str(settings.SCANS_DIR / f"scan_{scan_id}.xml")

        # Build structured parameter list
        args = ScanProfileBuilder.build_nmap_args(
            profile=profile,
            target_value=target_value,
            xml_output_path=xml_output_path,
            nmap_bin=settings.NMAP_PATH,
            custom_ports=custom_ports,
        )

        logger.info(f"Executing safe subprocess scan: {' '.join(args)}")

        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(), timeout=timeout_seconds
            )
            exit_code = process.returncode or 0
            stdout_str = stdout_data.decode(errors="replace")
            stderr_str = stderr_data.decode(errors="replace")
            return exit_code, xml_output_path, stdout_str, stderr_str

        except FileNotFoundError:
            logger.warning(
                f"Nmap binary '{settings.NMAP_PATH}' not found on system PATH. Generating simulated demo scan results."
            )
            # Write simulated XML output for demo fallback
            simulated_xml = SIMULATED_NMAP_XML_TEMPLATE.format(target_value=target_value)
            with open(xml_output_path, "w", encoding="utf-8") as f:
                f.write(simulated_xml)

            return (
                0,
                xml_output_path,
                "[DEMO MODE] Nmap executable not installed on host. Generated simulated scan results.",
                "",
            )

        except asyncio.TimeoutError:
            logger.error(f"Nmap scan process timed out after {timeout_seconds}s")
            return -1, xml_output_path, "", f"Scan process timed out after {timeout_seconds} seconds"

        except Exception as e:
            logger.error(f"Failed to execute Nmap subprocess: {str(e)}")
            return -1, xml_output_path, "", f"Failed to execute scan: {str(e)}"
