from typing import Dict, List, Optional
from app.validators.base import BaseValidator
from app.validators.http_validator import HTTPValidator
from app.validators.smb_validator import SMBValidator
from app.validators.ssh_validator import SSHValidator
from app.validators.tls_validator import TLSValidator


class ValidatorRegistry:
    _validators: Dict[str, BaseValidator] = {}

    @classmethod
    def register_default_validators(cls) -> None:
        """Registers all built-in non-destructive validator plugins."""
        cls.register(HTTPValidator())
        cls.register(TLSValidator())
        cls.register(SSHValidator())
        cls.register(SMBValidator())

    @classmethod
    def register(cls, validator: BaseValidator) -> None:
        cls._validators[validator.id] = validator

    @classmethod
    def get_validator(cls, validator_id: str) -> Optional[BaseValidator]:
        return cls._validators.get(validator_id)

    @classmethod
    def list_validators(cls) -> List[BaseValidator]:
        return list(cls._validators.values())

    @classmethod
    def find_validators_for_service(cls, service_name: str, port: int) -> List[BaseValidator]:
        return [v for v in cls._validators.values() if v.supports(service_name, port)]


# Initialize registry with default plugins
ValidatorRegistry.register_default_validators()
