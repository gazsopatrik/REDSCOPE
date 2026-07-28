from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.validation import ValidationApprove, ValidationCreate, ValidationRead
from app.services.validation_service import ValidationService, ValidationServiceError

router = APIRouter()


@router.get("/findings/{finding_id}/validations", response_model=List[ValidationRead])
async def list_finding_validations(
    finding_id: str, db: AsyncSession = Depends(get_db)
) -> List[ValidationRead]:
    return await ValidationService.get_validations_by_finding(db, finding_id)


@router.post("/findings/{finding_id}/validations", response_model=ValidationRead, status_code=status.HTTP_201_CREATED)
async def create_validation_task(
    finding_id: str, data: ValidationCreate, db: AsyncSession = Depends(get_db)
) -> ValidationRead:
    try:
        return await ValidationService.create_validation_task(db, finding_id, data.validator_id)
    except ValidationServiceError as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.post("/validations/{validation_id}/approve", response_model=ValidationRead)
async def approve_validation(
    validation_id: str, data: ValidationApprove, db: AsyncSession = Depends(get_db)
) -> ValidationRead:
    try:
        return await ValidationService.approve_validation(db, validation_id, approved_by=data.approved_by)
    except ValidationServiceError as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.post("/validations/{validation_id}/run", response_model=ValidationRead)
async def run_validation(
    validation_id: str, db: AsyncSession = Depends(get_db)
) -> ValidationRead:
    try:
        return await ValidationService.run_validation(db, validation_id)
    except ValidationServiceError as err:
        raise HTTPException(status_code=400, detail=str(err))
