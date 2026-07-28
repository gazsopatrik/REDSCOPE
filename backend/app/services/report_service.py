import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.finding import Finding
from app.models.host import Host
from app.models.project import Project
from app.models.report import Report, ReportFormat
from app.models.scan import Scan
from app.models.scope import Scope
from app.models.service import Service
from app.models.target import Target
from app.reporting.html_report import HTMLReportGenerator
from app.reporting.json_report import JSONReportGenerator
from app.reporting.markdown_report import MarkdownReportGenerator
from app.schemas.report import ReportCreate
from app.services.audit_service import AuditService
from app.services.project_service import ProjectService


class ReportServiceError(Exception):
    pass


class ReportService:
    @staticmethod
    async def get_reports_by_project(db: AsyncSession, project_id: str) -> List[Report]:
        result = await db.execute(
            select(Report).where(Report.project_id == project_id).order_by(Report.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_report_by_id(db: AsyncSession, report_id: str) -> Optional[Report]:
        result = await db.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def generate_report(
        db: AsyncSession, project_id: str, data: ReportCreate, actor: str = "system"
    ) -> Report:
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise ReportServiceError("Project not found.")

        # Fetch project scopes, targets, and findings
        scopes_res = await db.execute(select(Scope).where(Scope.project_id == project_id))
        scopes = [s.__dict__ for s in scopes_res.scalars().all()]

        targets_res = await db.execute(select(Target).where(Target.project_id == project_id))
        targets = [t.__dict__ for t in targets_res.scalars().all()]

        findings_res = await db.execute(
            select(Finding)
            .join(Service, Finding.service_id == Service.id)
            .join(Host, Service.host_id == Host.id)
            .join(Scan, Host.scan_id == Scan.id)
            .where(Scan.project_id == project_id)
            .order_by(Finding.risk_score.desc())
        )
        findings = [f.__dict__ for f in findings_res.scalars().all()]

        report_data = {
            "project": {
                "id": project.id,
                "name": project.name,
                "client_name": project.client_name,
                "status": project.status.value,
                "authorization_reference": project.authorization_reference,
            },
            "scopes": scopes,
            "targets": targets,
            "findings": findings,
        }

        report_id = str(uuid.uuid4())
        settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        if data.format == ReportFormat.HTML:
            file_path = str(settings.REPORTS_DIR / f"report_{report_id}.html")
            HTMLReportGenerator.generate_html_report(report_data, file_path)
        elif data.format == ReportFormat.MARKDOWN:
            file_path = str(settings.REPORTS_DIR / f"report_{report_id}.md")
            MarkdownReportGenerator.generate_markdown_report(report_data, file_path)
        else:
            file_path = str(settings.REPORTS_DIR / f"report_{report_id}.json")
            JSONReportGenerator.generate_json_report(report_data, file_path)

        report = Report(
            id=report_id,
            project_id=project_id,
            title=data.title,
            format=data.format,
            file_path=file_path,
            created_by=actor,
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)

        await AuditService.log_event(
            db=db,
            action="report_generated",
            entity_type="report",
            actor=actor,
            entity_id=report.id,
            project_id=project_id,
            details={"format": data.format.value, "file_path": file_path},
        )
        return report
