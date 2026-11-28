"""Budget business logic — CRUD + spending status calculation."""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.budgets.models import Budget, BudgetPeriod
from src.budgets.schemas import BudgetStatus
from src.categories.models import CategoryType
from src.categories.services import get_category
from src.core.exceptions import BadRequest, NotFound
from src.transactions.models import TransactionType
from src.transactions.repositories import (
    daily_expenses_in_range,
    spending_by_category_in_range,
    sum_by_type,
)


# ── Helpers ───────────────────────────────────────────────


def _current_period_range(budget: Budget, as_of: date | None = None) -> tuple[date, date]:
    """Return (start, end) of the current period window for a budget."""
    today = as_of or date.today()
    if budget.period == BudgetPeriod.weekly:
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif budget.period == BudgetPeriod.monthly:
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    else:  # yearly
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
    return start, end


# ── CRUD ──────────────────────────────────────────────────


async def list_budgets(
    db: AsyncSession, user_id: uuid.UUID
) -> list[Budget]:
    result = await db.execute(
        select(Budget)
        .options(selectinload(Budget.category))
        .where(Budget.user_id == user_id)
        .order_by(Budget.start_date)
    )
    return list(result.scalars().all())


async def get_budget(
    db: AsyncSession, budget_id: uuid.UUID, user_id: uuid.UUID
) -> Budget:
    result = await db.execute(
        select(Budget)
        .options(selectinload(Budget.category))
        .where(Budget.id == budget_id, Budget.user_id == user_id)
    )
    budget = result.scalar_one_or_none()
    if not budget:
        raise NotFound("Budget not found")
    return budget


async def _ensure_expense_category(
    db: AsyncSession, category_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    # Budgets track spending; an income category would always show 0 spent.
    category = await get_category(db, category_id, user_id)
    if category.type != CategoryType.expense:
        raise BadRequest("Budget category must be an expense category")


async def create_budget(
    db: AsyncSession, user_id: uuid.UUID, data: dict
) -> Budget:
    if data.get("category_id") is not None:
        await _ensure_expense_category(db, data["category_id"], user_id)
    budget = Budget(user_id=user_id, **data)
    db.add(budget)
    await db.flush()
    await db.refresh(budget, attribute_names=["category"])
    return budget


async def update_budget(
    db: AsyncSession, budget_id: uuid.UUID, user_id: uuid.UUID, data: dict
) -> Budget:
    budget = await get_budget(db, budget_id, user_id)
    if "category_id" in data and data["category_id"] is not None:
        await _ensure_expense_category(db, data["category_id"], user_id)
    nullable_fields = {"category_id", "end_date"}
    for k, v in data.items():
        if v is not None or k in nullable_fields:
            setattr(budget, k, v)
    if budget.end_date is not None and budget.end_date < budget.start_date:
        raise BadRequest("end_date must be on or after start_date")
    await db.flush()
    await db.refresh(budget, attribute_names=["category"])
    return budget


async def delete_budget(
    db: AsyncSession, budget_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    budget = await get_budget(db, budget_id, user_id)
    await db.delete(budget)
    await db.flush()


# ── Status calculation ────────────────────────────────────


def effective_window(budget: Budget, as_of: date | None = None) -> tuple[date, date, bool]:
    """Clamp the current period window to the budget's own start/end dates."""
    period_start, period_end = _current_period_range(budget, as_of)
    if budget.start_date > period_start:
        period_start = budget.start_date
    if budget.end_date is not None and budget.end_date < period_end:
        period_end = budget.end_date
    in_effect = budget.is_active and period_start <= period_end
    return period_start, period_end, in_effect


def _build_budget_status(budget: Budget, spent: Decimal) -> BudgetStatus:
    remaining = budget.limit_amount - spent
    percentage = (
        float(spent / budget.limit_amount * 100) if budget.limit_amount else 0.0
    )
    return BudgetStatus(
        **{
            **BudgetStatus.model_validate(budget).model_dump(),
            "spent": spent,
            "remaining": remaining,
            "percentage": round(percentage, 2),
        }
    )


async def calculate_status(
    db: AsyncSession, budget: Budget
) -> BudgetStatus:
    """Calculate how much has been spent vs. the budget limit."""
    period_start, period_end, in_effect = effective_window(budget)

    if not in_effect:
        spent = Decimal("0")
    elif budget.category_id:
        spent = await spending_by_category_in_range(
            db, budget.user_id, budget.category_id, period_start, period_end
        )
    else:
        spent = await sum_by_type(
            db, budget.user_id, TransactionType.expense, period_start, period_end
        )

    return _build_budget_status(budget, spent)


async def list_budgets_with_status(
    db: AsyncSession, user_id: uuid.UUID
) -> list[BudgetStatus]:
    budgets = await list_budgets(db, user_id)
    if not budgets:
        return []

    windows = [(b, *effective_window(b)) for b in budgets]
    active_windows = [(s, e) for _, s, e, ok in windows if ok]
    if not active_windows:
        return [_build_budget_status(b, Decimal("0")) for b in budgets]

    min_start = min(s for s, _ in active_windows)
    max_end = max(e for _, e in active_windows)
    daily_rows = await daily_expenses_in_range(db, user_id, min_start, max_end)

    statuses: list[BudgetStatus] = []
    for budget, period_start, period_end, in_effect in windows:
        if not in_effect:
            statuses.append(_build_budget_status(budget, Decimal("0")))
            continue
        spent = sum(
            (
                amt
                for cat_id, txn_date, amt in daily_rows
                if period_start <= txn_date <= period_end
                and (budget.category_id is None or cat_id == budget.category_id)
            ),
            Decimal("0"),
        )
        statuses.append(_build_budget_status(budget, spent))
    return statuses
