"""Analytics business logic — summaries, breakdowns, trends, forecast."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.analytics.schemas import (
    CategoryBreakdown,
    ForecastResponse,
    PeriodComparison,
    SummaryResponse,
    TrendPoint,
)
from src.categories.models import Category
from src.transactions.models import Transaction, TransactionType
from src.transactions.repositories import monthly_totals, sum_by_type


async def summary(
    db: AsyncSession,
    user_id: uuid.UUID,
    date_from: date | None = None,
    date_to: date | None = None,
) -> SummaryResponse:
    total_income = await sum_by_type(
        db, user_id, TransactionType.income, date_from, date_to
    )
    total_expense = await sum_by_type(
        db, user_id, TransactionType.expense, date_from, date_to
    )
    # Count
    stmt = select(func.count(Transaction.id)).where(Transaction.user_id == user_id)
    if date_from:
        stmt = stmt.where(Transaction.transaction_date >= date_from)
    if date_to:
        stmt = stmt.where(Transaction.transaction_date <= date_to)
    count = (await db.execute(stmt)).scalar() or 0

    return SummaryResponse(
        total_income=total_income,
        total_expense=total_expense,
        net=total_income - total_expense,
        transactions_count=count,
    )


async def by_category(
    db: AsyncSession,
    user_id: uuid.UUID,
    date_from: date | None = None,
    date_to: date | None = None,
    txn_type: TransactionType | None = TransactionType.expense,
) -> list[CategoryBreakdown]:
    stmt = (
        select(
            Transaction.category_id,
            Category.name,
            func.sum(Transaction.amount),
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .where(Transaction.user_id == user_id)
        .group_by(Transaction.category_id, Category.name)
    )
    if txn_type:
        stmt = stmt.where(Transaction.type == txn_type)
    if date_from:
        stmt = stmt.where(Transaction.transaction_date >= date_from)
    if date_to:
        stmt = stmt.where(Transaction.transaction_date <= date_to)

    raw_rows = (await db.execute(stmt)).all()
    rows = [(r[0], r[1], Decimal(str(r[2]))) for r in raw_rows]
    grand_total = sum(r[2] for r in rows) or Decimal("1")

    result = [
        CategoryBreakdown(
            category_id=str(cat_id) if cat_id else None,
            category_name=cat_name,
            total=total,
            percentage=round(float(total / grand_total * 100), 2),
        )
        for cat_id, cat_name, total in rows
    ]
    return sorted(result, key=lambda x: x.total, reverse=True)


async def trends(
    db: AsyncSession,
    user_id: uuid.UUID,
    months: int = 12,
) -> list[TrendPoint]:
    income_rows = await monthly_totals(db, user_id, TransactionType.income, months=months)
    expense_rows = await monthly_totals(db, user_id, TransactionType.expense, months=months)

    income_map = dict(income_rows)
    expense_map = dict(expense_rows)
    all_months = sorted(set(income_map) | set(expense_map))[-months:]

    return [
        TrendPoint(
            month=m,
            income=income_map.get(m, Decimal("0")),
            expense=expense_map.get(m, Decimal("0")),
        )
        for m in all_months
    ]


async def forecast(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> ForecastResponse:
    """Simple linear extrapolation from last 6 months."""
    inc = await monthly_totals(db, user_id, TransactionType.income, months=6)
    exp = await monthly_totals(db, user_id, TransactionType.expense, months=6)

    def _predict(data: list[tuple[str, Decimal]]) -> Decimal:
        if not data:
            return Decimal("0")
        values = [float(d[1]) for d in data]
        n = len(values)
        if n < 2:
            return Decimal(str(round(values[0], 2)))
        # Simple linear regression
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator else 0
        intercept = y_mean - slope * x_mean
        predicted = max(0, intercept + slope * n)
        return Decimal(str(round(predicted, 2)))

    today = date.today()
    if today.month == 12:
        next_m = f"{today.year + 1}-01"
    else:
        next_m = f"{today.year}-{today.month + 1:02d}"

    return ForecastResponse(
        next_month=next_m,
        predicted_income=_predict(inc),
        predicted_expense=_predict(exp),
    )


async def compare_periods(
    db: AsyncSession,
    user_id: uuid.UUID,
    current_start: date,
    current_end: date,
    previous_start: date,
    previous_end: date,
) -> PeriodComparison:
    cur_income = await sum_by_type(db, user_id, TransactionType.income, current_start, current_end)
    cur_expense = await sum_by_type(db, user_id, TransactionType.expense, current_start, current_end)
    prev_income = await sum_by_type(db, user_id, TransactionType.income, previous_start, previous_end)
    prev_expense = await sum_by_type(db, user_id, TransactionType.expense, previous_start, previous_end)

    def _pct(cur: Decimal, prev: Decimal) -> float:
        if prev == 0:
            return 100.0 if cur > 0 else 0.0
        return round(float((cur - prev) / prev * 100), 2)

    return PeriodComparison(
        current_income=cur_income,
        current_expense=cur_expense,
        previous_income=prev_income,
        previous_expense=prev_expense,
        income_change_pct=_pct(cur_income, prev_income),
        expense_change_pct=_pct(cur_expense, prev_expense),
    )
