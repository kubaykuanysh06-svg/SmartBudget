"""Deals API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_user, get_db
from src.deals import schemas, services

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=list[schemas.DealResponse])
async def list_deals(
    store: str | None = Query(None),
    category_id: uuid.UUID | None = Query(None),
    min_discount: float | None = Query(None),
    is_active: bool = Query(True),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    filters = schemas.DealFilter(
        store=store,
        category_id=category_id,
        min_discount=min_discount,
        is_active=is_active,
    )
    return await services.list_deals(db, filters, page, per_page)


@router.get("/personalized", response_model=list[schemas.DealResponse])
async def personalized_deals(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.personalized_deals(db, current_user.id, page, per_page)


@router.get("/price-history/{product}", response_model=list[schemas.PriceHistoryResponse])
async def price_history(
    product: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.get_price_history(db, current_user.id, product)
