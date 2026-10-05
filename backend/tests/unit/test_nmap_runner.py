import asyncio

import pytest
from app.models.scan import ScanProfile
from app.scanners.nmap_runner import NmapRunner
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


@pytest.mark.asyncio
async def test_nmap_timeout_kills_and_reaps_process(monkeypatch, tmp_path) -> None:
    class HangingProcess:
        returncode = None

        def __init__(self) -> None:
            self.killed = False
            self.communicate_calls = 0

        async def communicate(self):
            self.communicate_calls += 1
            if self.communicate_calls == 1:
                await asyncio.sleep(60)
            return b"", b""

        def kill(self) -> None:
            self.killed = True

    process = HangingProcess()

    async def create_process(*args, **kwargs):
        return process

    monkeypatch.setattr("app.scanners.nmap_runner.asyncio.create_subprocess_exec", create_process)
    monkeypatch.setattr("app.scanners.nmap_runner.settings.SCANS_DIR", tmp_path)

    exit_code, _, _, stderr = await NmapRunner.run_scan_async(
        "192.168.1.100", ScanProfile.QUICK_DISCOVERY, timeout_seconds=0.001
    )

    assert exit_code == -1
    assert "timed out" in stderr
    assert process.killed is True
    assert process.communicate_calls == 2
