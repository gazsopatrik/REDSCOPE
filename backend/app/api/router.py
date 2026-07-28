from fastapi import APIRouter
from app.api import audit_logs, health, projects, scans, scopes, targets

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health Check"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(scopes.router, tags=["Scopes"])
api_router.include_router(targets.router, tags=["Targets"])
api_router.include_router(scans.router, tags=["Scans"])
api_router.include_router(audit_logs.router, tags=["Audit Logs"])
