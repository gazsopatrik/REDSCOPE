import pytest
from app.models.scan import ScanProfile
from app.scanners.scan_profiles import ScanProfileBuilder
from app.security.command_policy import CommandPolicy, CommandPolicyError


def test_command_policy_valid_ports() -> None:
    res = CommandPolicy.validate_port_list("22, 80, 443, 8000-8080")
    assert res == "22,80,443,8000-8080"


def test_command_policy_invalid_ports() -> None:
    with pytest.raises(CommandPolicyError):
        CommandPolicy.validate_port_list("22; rm -rf /")

    with pytest.raises(CommandPolicyError):
        CommandPolicy.validate_port_list("70000")


def test_scan_profile_args_quick() -> None:
    args = ScanProfileBuilder.build_nmap_args(
        profile=ScanProfile.QUICK_DISCOVERY,
        target_value="192.168.1.100",
        xml_output_path="test_output.xml",
    )
    assert "nmap" in args[0]
    assert "-oX" in args
    assert "test_output.xml" in args
    assert "192.168.1.100" == args[-1]
