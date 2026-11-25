"""Budget business logic — CRUD + spending status calculation."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.budgets.models import Budget, BudgetPeriod
from src.budgets.schemas import BudgetStatus
from src.categories.services import get_category
from src.core.exceptions import NotFound
from src.transactions.repositories import spending_by_category_in_range


# ── Helpers ───────────────────────────────────────────────


def _current_period_range(budget: Budget) -> tuple[date, date]:
    """Return (start, end) of the current period window for a budget."""
    today = date.today()
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


async def create_budget(
    db: AsyncSession, user_id: uuid.UUID, data: dict
) -> Budget:
    if data.get("category_id") is not None:
        await get_category(db, data["category_id"], user_id)
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
        await get_category(db, data["category_id"], user_id)
    nullable_fields = {"category_id", "end_date"}
    for k, v in data.items():
        if v is not None or k in nullable_fields:
            setattr(budget, k, v)
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


async def calculate_status(
    db: AsyncSession, budget: Budget
) -> BudgetStatus:
    """Calculate how much has been spent vs. the budget limit."""
    period_start, period_end = _current_period_range(budget)

    if budget.category_id:
        spent = await spending_by_category_in_range(
            db, budget.user_id, budget.category_id, period_start, period_end
        )
    else:
        # Total budget across all categories
        from src.transactions.repositories import sum_by_type
        from src.transactions.models import TransactionType

        spent = await sum_by_type(
            db, budget.user_id, TransactionType.expense, period_start, period_end
        )

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


async def list_budgets_with_status(
    db: AsyncSession, user_id: uuid.UUID
) -> list[BudgetStatus]:
    budgets = await list_budgets(db, user_id)
    return [await calculate_status(db, b) for b in budgets]
