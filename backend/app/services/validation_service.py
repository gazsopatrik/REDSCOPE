from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.finding import Finding, FindingStatus
from app.models.host import Host
from app.models.scan import Scan
from app.models.service import Service
from app.models.target import ScopeStatus, Target
from app.models.validation import Validation, ValidationStatus
from app.scope.validator import ScopeValidator
from app.services.audit_service import AuditService
from app.services.scope_service import ScopeService
from app.validators.registry import ValidatorRegistry


class ValidationServiceError(Exception):
    pass


class ValidationService:
    @staticmethod
    async def get_validations_by_finding(db: AsyncSession, finding_id: str) -> List[Validation]:
        result = await db.execute(
            select(Validation).where(Validation.finding_id == finding_id).order_by(Validation.id.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_validation_by_id(db: AsyncSession, validation_id: str) -> Optional[Validation]:
        result = await db.execute(select(Validation).where(Validation.id == validation_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_validation_task(
        db: AsyncSession, finding_id: str, validator_id: str, actor: str = "system"
    ) -> Validation:
        validator = ValidatorRegistry.get_validator(validator_id)
        if not validator:
            raise ValidationServiceError(f"Validator '{validator_id}' not found in registry.")

        # Check finding existence
        result = await db.execute(select(Finding).where(Finding.id == finding_id))
        finding = result.scalar_one_or_none()
        if not finding:
            raise ValidationServiceError("Finding not found.")

        service_result = await db.execute(select(Service).where(Service.id == finding.service_id))
        service = service_result.scalar_one_or_none()
        if not service:
            raise ValidationServiceError("Associated service not found.")
        if not validator.supports(service.service_name or "", service.port):
            raise ValidationServiceError(
                f"Validator '{validator_id}' does not support service "
                f"'{service.service_name or 'unknown'}' on port {service.port}."
            )

        validation = Validation(
            finding_id=finding_id,
            validator_id=validator.id,
            validator_name=validator.name,
            risk_level=validator.risk_level,
            status=ValidationStatus.AWAITING_APPROVAL,
            requires_approval=True,
        )
        db.add(validation)
        await db.commit()
        await db.refresh(validation)

        return validation

    @staticmethod
    async def approve_validation(
        db: AsyncSession, validation_id: str, approved_by: str = "security_auditor"
    ) -> Validation:
        validation = await ValidationService.get_validation_by_id(db, validation_id)
        if not validation:
            raise ValidationServiceError("Validation task not found.")

        if validation.status != ValidationStatus.AWAITING_APPROVAL:
            raise ValidationServiceError(
                f"Cannot approve validation task in status '{validation.status.value}'."
            )

        validation.status = ValidationStatus.APPROVED
        validation.approved_by = approved_by
        validation.approved_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(validation)

        await AuditService.log_event(
            db=db,
            action="validation_approved",
            entity_type="validation",
            actor=approved_by,
            entity_id=validation.id,
            details={"validator_id": validation.validator_id, "finding_id": validation.finding_id},
        )
        return validation

    @staticmethod
    async def run_validation(db: AsyncSession, validation_id: str) -> Validation:
        validation = await ValidationService.get_validation_by_id(db, validation_id)
        if not validation:
            raise ValidationServiceError("Validation task not found.")

        if validation.status != ValidationStatus.APPROVED:
            raise ValidationServiceError(
                f"Cannot execute validation task in status '{validation.status.value}'. Explicit approval is required."
            )

        # 1. Fetch Target & Re-run Scope Verification Guard
        finding_res = await db.execute(
            select(Finding, Service, Host, Scan, Target)
            .join(Service, Finding.service_id == Service.id)
            .join(Host, Service.host_id == Host.id)
            .join(Scan, Host.scan_id == Scan.id)
            .join(Target, Scan.target_id == Target.id)
            .where(Finding.id == validation.finding_id)
        )
        row = finding_res.first()
        if not row:
            raise ValidationServiceError("Associated finding or target details missing.")

        finding, service, host, scan, target = row

        scopes = await ScopeService.get_scopes_by_project(db, scan.project_id)
        decision = ScopeValidator.evaluate_target_against_scopes(target.target_value, scopes)
        if decision.is_allowed:
            # The validator connects to the scanned host IP, which may differ from current DNS.
            decision = ScopeValidator.evaluate_target_against_scopes(host.ip_address, scopes)

        if not decision.is_allowed:
            validation.status = ValidationStatus.BLOCKED
            validation.finished_at = datetime.now(timezone.utc)
            validation.error_message = f"Validation BLOCKED: Scope check failed prior to execution ({decision.message})."
            await db.commit()
            await db.refresh(validation)
            await AuditService.log_event(
                db=db,
                action="validation_blocked",
                entity_type="validation",
                actor=validation.approved_by or "system",
                entity_id=validation.id,
                details={"reason": decision.message, "finding_id": validation.finding_id},
            )
            return validation

        # 2. Execute Validator Plugin
        validator = ValidatorRegistry.get_validator(validation.validator_id)
        if not validator:
            validation.status = ValidationStatus.FAILED
            validation.finished_at = datetime.now(timezone.utc)
            validation.error_message = "Validator plugin missing."
            await db.commit()
            await db.refresh(validation)
            await AuditService.log_event(
                db=db,
                action="validation_executed",
                entity_type="validation",
                actor=validation.approved_by or "system",
                entity_id=validation.id,
                details={
                    "status": validation.status.value,
                    "summary": "Validator plugin missing.",
                    "passed": False,
                },
            )
            return validation

        validation.status = ValidationStatus.RUNNING
        validation.started_at = datetime.now(timezone.utc)
        await db.commit()

        service_info = {
            "service_name": service.service_name,
            "product": service.product,
            "version": service.version,
            "tunnel": service.tunnel,
        }

        try:
            val_result = await validator.validate(
                target_ip=host.ip_address, port=service.port, service_info=service_info
            )
        except Exception as exc:
            validation.status = ValidationStatus.FAILED
            validation.finished_at = datetime.now(timezone.utc)
            validation.error_message = f"Validator execution failed: {exc}"
            await db.commit()
            await db.refresh(validation)
            await AuditService.log_event(
                db=db,
                action="validation_executed",
                entity_type="validation",
                actor=validation.approved_by or "system",
                entity_id=validation.id,
                details={
                    "status": validation.status.value,
                    "summary": "Validator execution failed unexpectedly.",
                    "passed": False,
                },
            )
            return validation

        validation.finished_at = datetime.now(timezone.utc)
        validation.evidence = val_result.evidence
        validation.error_message = val_result.error_message

        if val_result.passed:
            validation.status = ValidationStatus.PASSED
            finding.status = FindingStatus.VALIDATED
            finding.confidence_score = min(finding.confidence_score + val_result.confidence_delta, 100.0)
            finding.evidence = {**(finding.evidence or {}), "validation_proof": val_result.evidence}
        else:
            validation.status = ValidationStatus.FAILED if val_result.status == "failed" else ValidationStatus.INCONCLUSIVE

        await db.commit()
        await db.refresh(validation)

        await AuditService.log_event(
            db=db,
            action="validation_executed",
            entity_type="validation",
            actor=validation.approved_by or "system",
            entity_id=validation.id,
            details={
                "status": validation.status.value,
                "summary": val_result.summary,
                "passed": val_result.passed,
            },
        )
        return validation
