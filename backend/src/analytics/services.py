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
    ReceiptBudget,
    ReceiptMerchant,
    ReceiptReport,
    SummaryResponse,
    TrendPoint,
)
from src.budgets.services import effective_window, list_budgets
from src.categories.models import Category
from src.core.exceptions import BadRequest
from src.transactions.models import Transaction, TransactionType
from src.transactions.repositories import (
    category_amount_rows, daily_expenses_in_range, monthly_totals, sum_by_type,
)


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
    *,
    only_receipts: bool = False,
) -> list[CategoryBreakdown]:
    amounts = category_amount_rows(user_id, date_from, date_to, txn_type, only_receipts=only_receipts)
    stmt = (
        select(
            Category.id,
            Category.name,
            func.sum(amounts.c.amount),
        )
        .select_from(amounts)
        .outerjoin(Category, amounts.c.category_id == Category.id)
        .group_by(Category.id, Category.name)
    )

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


async def receipt_report(
    db: AsyncSession,
    user_id: uuid.UUID,
    date_from: date,
    date_to: date,
    previous_from: date | None = None,
    previous_to: date | None = None,
    *,
    budget_receipts_only: bool = True,
) -> ReceiptReport:
    if date_from > date_to or (previous_from is None) != (previous_to is None):
        raise BadRequest("Invalid report date range")
    if previous_from and previous_to and not previous_from <= previous_to < date_from:
        raise BadRequest("Invalid previous date range")

    criteria = (
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.expense,
        Transaction.ai_metadata["receipt"].is_not(None),
    )
    merchant = func.lower(func.trim(Transaction.merchant))
    store_rows = await db.execute(
        select(func.min(Transaction.merchant), func.sum(Transaction.amount))
        .where(*criteria, Transaction.transaction_date.between(date_from, date_to))
        .group_by(merchant)
        .order_by(func.sum(Transaction.amount).desc(), merchant)
    )
    merchants = [ReceiptMerchant(name=name, total=amount) for name, amount in store_rows]
    total = sum((row.total for row in merchants), Decimal(0))
    categories = await by_category(db, user_id, date_from, date_to, only_receipts=True)

    budgets = await list_budgets(db, user_id)
    anchor = min(date_to, date.today())
    windows = [
        (budget, start, end)
        for budget in budgets
        for start, end, active in [effective_window(budget, anchor)]
        if active and start <= date_to and end >= date_from
    ]
    budget_rows = []
    if windows:
        daily = await daily_expenses_in_range(
            db, user_id, min(start for _, start, _ in windows),
            max(end for _, _, end in windows), only_receipts=budget_receipts_only,
        )
        for budget, start, end in windows:
            spent = sum((
                amount for category_id, day, amount in daily
                if start <= day <= end and (budget.category_id is None or category_id == budget.category_id)
            ), Decimal(0))
            budget_rows.append(ReceiptBudget(
                category_name=budget.category.name if budget.category else None,
                date_from=start, date_to=end, limit=budget.limit_amount, spent=spent,
                remaining=budget.limit_amount - spent,
            ))

    previous = None
    if previous_from and previous_to:
        previous = await db.scalar(
            select(func.sum(Transaction.amount)).where(
                *criteria, Transaction.transaction_date.between(previous_from, previous_to)
            )
        )
    change = total - previous if previous is not None else None
    change_pct = (change / previous * 100).quantize(Decimal("0.01")) if previous and change is not None else None
    return ReceiptReport(
        total=total, merchants=merchants, categories=categories,
        highest_category=categories[0] if categories else None,
        budgets=budget_rows, previous_total=previous, change=change, change_pct=change_pct,
    )
