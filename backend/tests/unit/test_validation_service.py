from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.models.validation import ValidationStatus
from app.services.audit_service import AuditService
from app.services.scope_service import ScopeService
from app.services.validation_service import ValidationService, ValidationServiceError
from app.scope.validator import ScopeValidator
from app.validators.registry import ValidatorRegistry


@pytest.mark.asyncio
async def test_create_validation_rejects_incompatible_service(monkeypatch) -> None:
    db = SimpleNamespace(
        execute=AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: SimpleNamespace(service_id="service-1")),
            SimpleNamespace(scalar_one_or_none=lambda: SimpleNamespace(service_name="ssh", port=22)),
        ]),
        commit=AsyncMock(),
    )
    validator = SimpleNamespace(supports=lambda service_name, port: False)
    monkeypatch.setattr(ValidatorRegistry, "get_validator", lambda _id: validator)

    with pytest.raises(ValidationServiceError, match="does not support service"):
        await ValidationService.create_validation_task(db, "finding-1", "http-validator")

    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_plugin_exception_finishes_validation_task(monkeypatch) -> None:
    validation = SimpleNamespace(
        id="validation-1",
        finding_id="finding-1",
        validator_id="test-validator",
        status=ValidationStatus.APPROVED,
        approved_by="auditor",
        finished_at=None,
        error_message=None,
    )
    service = SimpleNamespace(
        service_name="http", port=80, product=None, version=None, tunnel=None
    )
    row = (
        SimpleNamespace(),
        service,
        SimpleNamespace(ip_address="192.0.2.10"),
        SimpleNamespace(project_id="project-1"),
        SimpleNamespace(target_value="192.0.2.10"),
    )
    db = SimpleNamespace(
        execute=AsyncMock(return_value=SimpleNamespace(first=lambda: row)),
        commit=AsyncMock(),
        refresh=AsyncMock(),
    )
    validator = SimpleNamespace(validate=AsyncMock(side_effect=RuntimeError("probe failed")))
    monkeypatch.setattr(
        ValidationService, "get_validation_by_id", AsyncMock(return_value=validation)
    )
    monkeypatch.setattr(ValidatorRegistry, "get_validator", lambda _id: validator)
    audit_log = AsyncMock()
    monkeypatch.setattr(AuditService, "log_event", audit_log)
    monkeypatch.setattr(ScopeService, "get_scopes_by_project", AsyncMock(return_value=[]))
    monkeypatch.setattr(
        ScopeValidator, "evaluate_target_against_scopes",
        lambda _target, _scopes: SimpleNamespace(is_allowed=True),
    )

    result = await ValidationService.run_validation(db, validation.id)

    assert result.status == ValidationStatus.FAILED
    assert result.finished_at is not None
    assert "probe failed" in result.error_message
    assert db.commit.await_count == 2
    db.refresh.assert_awaited_once_with(validation)
    audit_log.assert_awaited_once()
    assert audit_log.await_args.kwargs["details"] == {
        "status": "failed",
        "summary": "Validator execution failed unexpectedly.",
        "passed": False,
    }

@pytest.mark.asyncio
async def test_missing_plugin_finishes_and_audits_validation(monkeypatch) -> None:
    validation = SimpleNamespace(
        id="validation-2",
        finding_id="finding-2",
        validator_id="removed-validator",
        status=ValidationStatus.APPROVED,
        approved_by="auditor",
        finished_at=None,
        error_message=None,
    )
    row = (
        SimpleNamespace(),
        SimpleNamespace(),
        SimpleNamespace(),
        SimpleNamespace(project_id="project-1"),
        SimpleNamespace(target_value="192.0.2.10"),
    )
    db = SimpleNamespace(
        execute=AsyncMock(return_value=SimpleNamespace(first=lambda: row)),
        commit=AsyncMock(),
        refresh=AsyncMock(),
    )
    audit_log = AsyncMock()
    monkeypatch.setattr(
        ValidationService, "get_validation_by_id", AsyncMock(return_value=validation)
    )
    monkeypatch.setattr(ValidatorRegistry, "get_validator", lambda _id: None)
    monkeypatch.setattr(ScopeService, "get_scopes_by_project", AsyncMock(return_value=[]))
    monkeypatch.setattr(
        ScopeValidator, "evaluate_target_against_scopes",
        lambda _target, _scopes: SimpleNamespace(is_allowed=True),
    )
    monkeypatch.setattr(AuditService, "log_event", audit_log)

    result = await ValidationService.run_validation(db, validation.id)

    assert result.status == ValidationStatus.FAILED
    assert result.finished_at is not None
    assert result.error_message == "Validator plugin missing."
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(validation)
    audit_log.assert_awaited_once()
    assert audit_log.await_args.kwargs["details"] == {
        "status": "failed",
        "summary": "Validator plugin missing.",
        "passed": False,
    }

@pytest.mark.asyncio
async def test_validation_blocks_scanned_host_outside_scope(monkeypatch) -> None:
    validation = SimpleNamespace(
        id="validation-3",
        finding_id="finding-3",
        validator_id="http-validator",
        status=ValidationStatus.APPROVED,
        error_message=None,
    )
    host_ip = "203.0.113.10"
    row = (
        SimpleNamespace(),
        SimpleNamespace(),
        SimpleNamespace(ip_address=host_ip),
        SimpleNamespace(project_id="project-1"),
        SimpleNamespace(target_value="authorized.example"),
    )
    db = SimpleNamespace(
        execute=AsyncMock(return_value=SimpleNamespace(first=lambda: row)),
        commit=AsyncMock(),
        refresh=AsyncMock(),
    )
    validator = SimpleNamespace(validate=AsyncMock())
    checked_targets = []

    def evaluate(value, _scopes):
        checked_targets.append(value)
        return SimpleNamespace(
            is_allowed=value != host_ip,
            message="Scanned host IP outside scope",
        )

    monkeypatch.setattr(
        ValidationService, "get_validation_by_id", AsyncMock(return_value=validation)
    )
    monkeypatch.setattr(ScopeService, "get_scopes_by_project", AsyncMock(return_value=[]))
    monkeypatch.setattr(ScopeValidator, "evaluate_target_against_scopes", evaluate)
    monkeypatch.setattr(ValidatorRegistry, "get_validator", lambda _id: validator)

    result = await ValidationService.run_validation(db, validation.id)

    assert checked_targets == ["authorized.example", host_ip]
    assert result.status == ValidationStatus.BLOCKED
    assert "Scanned host IP outside scope" in result.error_message
    validator.validate.assert_not_awaited()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(validation)
