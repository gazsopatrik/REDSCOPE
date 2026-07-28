import pytest
from app.validators.http_validator import HTTPValidator
from app.validators.registry import ValidatorRegistry
from app.validators.ssh_validator import SSHValidator


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
