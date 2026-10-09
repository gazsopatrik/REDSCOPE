import pytest
from app.validators.http_validator import HTTPValidator, build_http_endpoint_url
from app.validators.registry import ValidatorRegistry
from app.validators.ssh_validator import SSHValidator
from app.validators.smb_validator import SMBValidator
from app.validators.tls_validator import TLSValidator


def test_validator_registry_lookup() -> None:
    validators = ValidatorRegistry.list_validators()
    assert len(validators) >= 4

    http_val = ValidatorRegistry.get_validator("http_security_header_check")
    assert http_val is not None
    assert http_val.destructive is False


def test_validator_supports_query() -> None:
    http_val = HTTPValidator()
    assert http_val.supports("http", 80) is True
    assert http_val.supports("https", 443) is True
    assert http_val.supports("ftp", 21) is False

    ssh_val = SSHValidator()
    assert ssh_val.supports("ssh", 22) is True
    assert ssh_val.supports("http", 80) is False


def test_http_endpoint_url_formats_ip_literals() -> None:
    assert build_http_endpoint_url("192.0.2.10", 8080, "http") == "http://192.0.2.10:8080/"
    assert build_http_endpoint_url("2001:db8::10", 8443, "https") == "https://[2001:db8::10]:8443/"


@pytest.mark.asyncio
async def test_tls_validator_closes_connection_after_certificate_error(monkeypatch) -> None:
    class BrokenSSLObject:
        def getpeercert(self, binary_form=False):
            raise ValueError("malformed certificate")

    class Writer:
        def __init__(self) -> None:
            self.closed = False
            self.waited = False

        def get_extra_info(self, name):
            return BrokenSSLObject() if name == "ssl_object" else None

        def close(self) -> None:
            self.closed = True

        async def wait_closed(self) -> None:
            self.waited = True

    writer = Writer()

    async def open_connection(*args, **kwargs):
        return object(), writer

    monkeypatch.setattr("app.validators.tls_validator.asyncio.open_connection", open_connection)
    result = await TLSValidator().validate("192.0.2.10", 443, {})

    assert result.passed is False
    assert writer.closed is True
    assert writer.waited is True


@pytest.mark.asyncio
async def test_ssh_validator_closes_connection_after_banner_timeout(monkeypatch) -> None:
    class Reader:
        async def readline(self):
            raise TimeoutError("banner timeout")

    class Writer:
        def __init__(self) -> None:
            self.closed = False
            self.waited = False

        def close(self) -> None:
            self.closed = True

        async def wait_closed(self) -> None:
            self.waited = True

    writer = Writer()

    async def open_connection(*args, **kwargs):
        return Reader(), writer

    monkeypatch.setattr("app.validators.ssh_validator.asyncio.open_connection", open_connection)
    result = await SSHValidator().validate("192.0.2.10", 22, {})

    assert result.passed is False
    assert writer.closed is True
    assert writer.waited is True


@pytest.mark.asyncio
async def test_smb_validator_sends_complete_packet_and_closes_after_timeout(monkeypatch) -> None:
    class Reader:
        async def read(self, size):
            raise TimeoutError("SMB response timeout")

    class Writer:
        def __init__(self) -> None:
            self.packet = b""
            self.closed = False
            self.waited = False

        def write(self, packet: bytes) -> None:
            self.packet = packet

        async def drain(self) -> None:
            pass

        def close(self) -> None:
            self.closed = True

        async def wait_closed(self) -> None:
            self.waited = True

    writer = Writer()

    async def open_connection(*args, **kwargs):
        return Reader(), writer

    monkeypatch.setattr("app.validators.smb_validator.asyncio.open_connection", open_connection)
    result = await SMBValidator().validate("192.0.2.10", 445, {})

    declared_payload_length = int.from_bytes(writer.packet[1:4], "big")
    assert declared_payload_length == len(writer.packet) - 4
    assert result.passed is False
    assert writer.closed is True
    assert writer.waited is True
