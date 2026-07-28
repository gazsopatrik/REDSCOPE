from typing import List, Optional
from app.models.scan import ScanProfile
from app.security.command_policy import CommandPolicy


class ScanProfileBuilder:
    @staticmethod
    def build_nmap_args(
        profile: ScanProfile,
        target_value: str,
        xml_output_path: str,
        nmap_bin: str = "nmap",
        custom_ports: Optional[str] = None,
    ) -> List[str]:
        """
        Builds a safe, structured parameter list for Nmap invocation.
        Returns a list array suitable for asyncio.create_subprocess_exec (shell=False).
        """
        base_args = [nmap_bin, "-oX", xml_output_path, "--open", "-T3"]

        if profile == ScanProfile.QUICK_DISCOVERY:
            # Fast ping & top 100 ports
            base_args.extend(["-sV", "--version-light", "--top-ports", "100"])

        elif profile == ScanProfile.STANDARD_SERVICE:
            # Standard service & banner detection
            base_args.extend(["-sV", "--version-intensity", "5", "-O"])

        elif profile == ScanProfile.FULL_TCP:
            # All 65,535 TCP ports
            base_args.extend(["-sV", "-p-"])

        elif profile == ScanProfile.SELECTED_PORTS:
            if not custom_ports:
                # Default fallback ports if custom string is omitted
                base_args.extend(["-sV", "-p", "21,22,80,443,445,3306,3389,8080,8443"])
            else:
                validated_ports = CommandPolicy.validate_port_list(custom_ports)
                base_args.extend(["-sV", "-p", validated_ports])

        elif profile == ScanProfile.UDP_COMMON:
            # Common UDP services scan
            base_args.extend(["-sU", "--top-ports", "20", "-sV"])

        else:
            base_args.extend(["-sV", "--top-ports", "100"])

        # Target address appended as final argument
        base_args.append(target_value)
        return base_args
