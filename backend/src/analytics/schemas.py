"""Analytics Pydantic schemas."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net: Decimal
    transactions_count: int


class CategoryBreakdown(BaseModel):
    category_id: str | None = None
    category_name: str | None = None
    total: Decimal
    percentage: float


class TrendPoint(BaseModel):
    month: str  # YYYY-MM
    income: Decimal
    expense: Decimal


class ForecastResponse(BaseModel):
    next_month: str
    predicted_income: Decimal
    predicted_expense: Decimal


class PeriodComparison(BaseModel):
    current_income: Decimal
    current_expense: Decimal
    previous_income: Decimal
    previous_expense: Decimal
    income_change_pct: float
    expense_change_pct: float
