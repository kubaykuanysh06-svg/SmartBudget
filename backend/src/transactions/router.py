"""Transaction API endpoints."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_user, get_db
from src.transactions import schemas, services
from src.transactions.models import TransactionType

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=schemas.TransactionResponse, status_code=201)
async def create_transaction(
    body: schemas.TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.create_transaction(
        db, current_user.id, body.model_dump()
    )


@router.get("", response_model=schemas.PaginatedTransactions)
async def list_transactions(
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    category_id: uuid.UUID | None = Query(None),
    type: TransactionType | None = Query(None),
    merchant_search: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = schemas.TransactionFilter(
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        type=type,
        merchant_search=merchant_search,
    )
    return await services.list_transactions(db, current_user.id, filters, page, per_page)


@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
async def get_transaction(
    transaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.get_transaction(db, transaction_id, current_user.id)


@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
async def update_transaction(
    transaction_id: uuid.UUID,
    body: schemas.TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.update_transaction(
        db, transaction_id, current_user.id, body.model_dump(exclude_unset=True)
    )


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await services.delete_transaction(db, transaction_id, current_user.id)


@router.post("/import", response_model=list[schemas.TransactionResponse])
async def import_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    content = (await file.read()).decode("utf-8")
    return await services.import_csv(db, current_user.id, content)
