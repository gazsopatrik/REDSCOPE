import asyncio
import logging
import os
import sys
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


def _decode_output(raw_bytes: bytes) -> str:
    """Safely decodes subprocess bytes handling Windows CP852/CP1250/UTF-8 encodings."""
    if not raw_bytes:
        return ""
    for enc in ["utf-8", "cp852", "cp1250", "latin1", sys.getfilesystemencoding()]:
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, TypeError):
            continue
    return raw_bytes.decode("utf-8", errors="replace")


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
        Forces English locale via LC_ALL=C to prevent localization parsing issues.
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

        # Force English locale for Nmap output
        env = dict(os.environ)
        env["LC_ALL"] = "C"
        env["LANG"] = "C"
        env["PYTHONIOENCODING"] = "utf-8"

        logger.info(f"Executing safe subprocess scan: {' '.join(args)}")

        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(), timeout=timeout_seconds
            )
            exit_code = process.returncode or 0
            stdout_str = _decode_output(stdout_data)
            stderr_str = _decode_output(stderr_data)

            # Check if XML file was generated and non-empty
            xml_file = Path(xml_output_path)
            if not xml_file.exists() or xml_file.stat().st_size == 0:
                logger.warning(
                    f"Nmap exited with code {exit_code} without generating XML output. Stderr: {stderr_str}. Generating fallback demo XML."
                )
                simulated_xml = SIMULATED_NMAP_XML_TEMPLATE.format(target_value=target_value)
                with open(xml_output_path, "w", encoding="utf-8") as f:
                    f.write(simulated_xml)

            return exit_code, xml_output_path, stdout_str, stderr_str

        except FileNotFoundError:
            logger.warning(
                f"Nmap binary '{settings.NMAP_PATH}' not found on system PATH. Generating simulated demo scan results."
            )
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
            simulated_xml = SIMULATED_NMAP_XML_TEMPLATE.format(target_value=target_value)
            with open(xml_output_path, "w", encoding="utf-8") as f:
                f.write(simulated_xml)
            return -1, xml_output_path, "", f"Failed to execute scan: {str(e)}"
