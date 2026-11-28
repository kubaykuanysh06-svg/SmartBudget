"""Analytics API endpoints."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.analytics import receipt_details, schemas, services
from src.core.dependencies import get_current_user, get_db
from src.transactions.models import TransactionType

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/receipt-details")
async def get_receipt_details(
    date_from: date, date_to: date,
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user),
):
    return await receipt_details.deep_report(db, current_user.id, date_from, date_to)


@router.get("/receipt-lines")
async def get_receipt_lines(
    date_from: date, date_to: date, group: receipt_details.Group, key: str = Query(max_length=900),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user),
):
    return await receipt_details.drilldown(db, current_user.id, date_from, date_to, group, key, offset)


@router.get("/receipts", response_model=schemas.ReceiptReport)
async def get_receipt_report(
    date_from: date,
    date_to: date,
    previous_from: date | None = None,
    previous_to: date | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.receipt_report(db, current_user.id, date_from, date_to, previous_from, previous_to)


@router.get("/summary", response_model=schemas.SummaryResponse)
async def get_summary(
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.summary(db, current_user.id, date_from, date_to)


@router.get("/by-category", response_model=list[schemas.CategoryBreakdown])
async def get_by_category(
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    type: TransactionType | None = Query(TransactionType.expense),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.by_category(db, current_user.id, date_from, date_to, type)


@router.get("/trends", response_model=list[schemas.TrendPoint])
async def get_trends(
    months: int = Query(12, ge=1, le=60),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.trends(db, current_user.id, months)


@router.get("/forecast", response_model=schemas.ForecastResponse)
async def get_forecast(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.forecast(db, current_user.id)


@router.get("/compare", response_model=schemas.PeriodComparison)
async def compare(
    current_start: date = Query(...),
    current_end: date = Query(...),
    previous_start: date = Query(...),
    previous_end: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.compare_periods(
        db, current_user.id,
        current_start, current_end,
        previous_start, previous_end,
    )
