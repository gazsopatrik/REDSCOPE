import shutil
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db

router = APIRouter()


@router.get("/health")
async def check_health(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    # Check Database connection
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check Nmap presence
    nmap_path = shutil.which(settings.NMAP_PATH)
    nmap_installed = nmap_path is not None

    status = "healthy" if (db_ok and nmap_installed) else "degraded"

    return {
        "status": status,
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "components": {
            "database": {
                "connected": db_ok,
                "url_type": settings.DATABASE_URL.split(":")[0]
            },
            "nmap": {
                "installed": nmap_installed,
                "path": nmap_path or "Not found in PATH"
            }
        }
    }
