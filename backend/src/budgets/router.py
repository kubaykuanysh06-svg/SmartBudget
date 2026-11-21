"""Budget API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.budgets import schemas, services
from src.core.dependencies import get_current_user, get_db

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[schemas.BudgetResponse])
async def list_budgets(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.list_budgets(db, current_user.id)


@router.get("/status", response_model=list[schemas.BudgetStatus])
async def list_budgets_status(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.list_budgets_with_status(db, current_user.id)


@router.post("", response_model=schemas.BudgetResponse, status_code=201)
async def create_budget(
    body: schemas.BudgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.create_budget(
        db, current_user.id, body.model_dump()
    )


@router.put("/{budget_id}", response_model=schemas.BudgetResponse)
async def update_budget(
    budget_id: uuid.UUID,
    body: schemas.BudgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.update_budget(
        db, budget_id, current_user.id, body.model_dump(exclude_unset=True)
    )
