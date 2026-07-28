from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ValidationResult:
    passed: bool
    status: str  # passed, failed, inconclusive
    summary: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    confidence_delta: float = 0.0
    risk_delta: float = 0.0
    error_message: Optional[str] = None


class BaseValidator(ABC):
    id: str
    name: str
    description: str
    supported_services: List[str]
    risk_level: str = "low"
    requires_approval: bool = True
    destructive: bool = False  # Strictly False for all non-destructive MVP validators

    @abstractmethod
    def supports(self, service_name: str, port: int) -> bool:
        """Returns True if this validator supports the target service and port."""
        pass

    @abstractmethod
    async def validate(self, target_ip: str, port: int, service_info: Dict[str, Any]) -> ValidationResult:
        """Executes non-destructive check against the target."""
        pass
