"""Analytics Pydantic schemas."""

from __future__ import annotations

from datetime import date
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


class ReceiptMerchant(BaseModel):
    name: str | None
    total: Decimal


class ReceiptBudget(BaseModel):
    category_name: str | None
    date_from: date
    date_to: date
    limit: Decimal
    spent: Decimal
    remaining: Decimal


class ReceiptReport(BaseModel):
    total: Decimal
    merchants: list[ReceiptMerchant]
    categories: list[CategoryBreakdown]
    highest_category: CategoryBreakdown | None
    budgets: list[ReceiptBudget]
    previous_total: Decimal | None
    change: Decimal | None
    change_pct: Decimal | None
