import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.host import Host
from app.models.scan import Scan, ScanProfile, ScanStatus
from app.models.service import Service
from app.models.target import ScopeStatus
from app.schemas.scan import ScanCreate
from app.scanners.nmap_parser import NmapXMLParser
from app.scanners.nmap_runner import NmapRunner
from app.scanners.scan_profiles import ScanProfileBuilder
from app.services.audit_service import AuditService
from app.services.target_service import TargetService


class ScanServiceError(Exception):
    pass


class ScanService:
    @staticmethod
    async def get_scans_by_project(db: AsyncSession, project_id: str) -> List[Scan]:
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(Scan)
            .options(selectinload(Scan.hosts).selectinload(Host.services))
            .where(Scan.project_id == project_id)
            .order_by(Scan.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_scan_by_id(db: AsyncSession, scan_id: str) -> Optional[Scan]:
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(Scan)
            .options(selectinload(Scan.hosts).selectinload(Host.services))
            .where(Scan.id == scan_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_and_run_scan(
        db: AsyncSession, project_id: str, data: ScanCreate, actor: str = "system"
    ) -> Scan:
        # 1. Fetch Target and enforce Pre-Scan Scope Validation
        target = await TargetService.get_target_by_id(db, data.target_id)
        if not target or target.project_id != project_id:
            raise ScanServiceError("Target not found or does not belong to project.")

        # Re-verify scope before scanning
        target = await TargetService.validate_target_scope(db, target.id, actor=actor)
        if not target or target.scope_status != ScopeStatus.ALLOWED:
            raise ScanServiceError(
                f"Scan DENIED: Target '{target.target_value if target else data.target_id}' is out-of-scope ({target.scope_validation_message if target else ''})."
            )

        # 2. Build command preview formatted for PowerShell / CMD execution
        raw_args = ScanProfileBuilder.build_nmap_args(
            profile=data.profile,
            target_value=target.target_value,
            xml_output_path="[OUTPUT_PATH].xml",
            custom_ports=data.custom_ports,
        )
        preview_args = list(raw_args)
        if preview_args and " " in preview_args[0]:
            preview_args[0] = f'& "{preview_args[0]}"'
        cmd_preview = " ".join(preview_args)

        # 3. Create Scan Record in RUNNING state
        scan = Scan(
            project_id=project_id,
            target_id=target.id,
            profile=data.profile,
            status=ScanStatus.RUNNING,
            command_preview=cmd_preview,
            custom_ports=data.custom_ports,
            created_by=actor,
            started_at=datetime.now(timezone.utc),
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)

        await AuditService.log_event(
            db=db,
            action="scan_started",
            entity_type="scan",
            actor=actor,
            entity_id=scan.id,
            project_id=project_id,
            details={"target": target.target_value, "profile": data.profile.value, "command": cmd_preview},
        )

        # 4. Dispatch Async Background Task for Nmap execution
        asyncio.create_task(
            ScanService._execute_scan_background(
                scan_id=scan.id,
                target_id=target.id,
                project_id=project_id,
                target_value=target.target_value,
                profile=data.profile,
                custom_ports=data.custom_ports,
                actor=actor,
            )
        )

        res = await ScanService.get_scan_by_id(db, scan.id)
        return res if res else scan

    @staticmethod
    async def _execute_scan_background(
        scan_id: str,
        target_id: str,
        project_id: str,
        target_value: str,
        profile: ScanProfile,
        custom_ports: Optional[str] = None,
        actor: str = "system",
    ):
        """Asynchronous worker that executes Nmap and updates DB status upon completion."""
        try:
            exit_code, xml_path, stdout_str, stderr_str = await NmapRunner.run_scan_async(
                target_value=target_value,
                profile=profile,
                custom_ports=custom_ports,
            )
        except Exception as run_err:
            async with AsyncSessionLocal() as db:
                scan = await ScanService.get_scan_by_id(db, scan_id)
                if scan:
                    scan.status = ScanStatus.FAILED
                    scan.error_message = f"Subprocess error: {str(run_err)}"
                    await db.commit()
            return

        async with AsyncSessionLocal() as db:
            scan = await ScanService.get_scan_by_id(db, scan_id)
            if not scan:
                return

            scan.finished_at = datetime.now(timezone.utc)
            scan.exit_code = exit_code
            scan.xml_output_path = xml_path
            scan.status = ScanStatus.PARSING
            await db.commit()

            try:
                parsed_result = NmapXMLParser.parse_xml_file(xml_path)
                for p_host in parsed_result.hosts:
                    host_db = Host(
                        scan_id=scan.id,
                        ip_address=p_host.ip_address,
                        hostname=p_host.hostname,
                        mac_address=p_host.mac_address,
                        vendor=p_host.vendor,
                        state=p_host.state,
                        os_name=p_host.os_name,
                        os_accuracy=p_host.os_accuracy,
                    )
                    db.add(host_db)
                    await db.flush()

                    for p_svc in p_host.services:
                        svc_db = Service(
                            host_id=host_db.id,
                            protocol=p_svc.protocol,
                            port=p_svc.port,
                            state=p_svc.state,
                            service_name=p_svc.service_name,
                            product=p_svc.product,
                            version=p_svc.version,
                            extra_info=p_svc.extra_info,
                            tunnel=p_svc.tunnel,
                            cpe=p_svc.cpe,
                            confidence=p_svc.confidence,
                            banner=p_svc.banner,
                        )
                        db.add(svc_db)

                target = await TargetService.get_target_by_id(db, target_id)
                if target:
                    target.last_scanned_at = datetime.now(timezone.utc)

                scan.status = ScanStatus.COMPLETED
                await db.commit()

                await AuditService.log_event(
                    db=db,
                    action="scan_completed",
                    entity_type="scan",
                    actor=actor,
                    entity_id=scan.id,
                    project_id=project_id,
                    details={"hosts_found": len(parsed_result.hosts)},
                )

            except Exception as parse_err:
                scan.status = ScanStatus.FAILED
                scan.error_message = f"Scan error: {str(parse_err)}"
                await db.commit()
