"""Deals business logic."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.deals.models import Deal, PriceHistory
from src.deals.schemas import DealFilter, DealResponse, PriceHistoryResponse


async def list_deals(
    db: AsyncSession,
    filters: DealFilter,
    page: int = 1,
    per_page: int = 20,
) -> list[DealResponse]:
    stmt = select(Deal).where(Deal.is_active == filters.is_active)
    if filters.store:
        stmt = stmt.where(Deal.store.ilike(f"%{filters.store}%"))
    if filters.category_id:
        stmt = stmt.where(Deal.category_id == filters.category_id)
    if filters.min_discount is not None:
        stmt = stmt.where(Deal.discount_percent >= filters.min_discount)

    stmt = (
        stmt.order_by(Deal.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    return [DealResponse.model_validate(d) for d in result.scalars().all()]


async def personalized_deals(
    db: AsyncSession,
    user_id: uuid.UUID,
    page: int = 1,
    per_page: int = 20,
) -> list[DealResponse]:
    """Return active deals matching the user's top spending categories."""
    from src.transactions.repositories import sum_by_category
    from src.transactions.models import TransactionType

    cat_spending = await sum_by_category(
        db, user_id, txn_type=TransactionType.expense
    )
    top_cat_ids = [
        cid for cid, _ in sorted(cat_spending, key=lambda x: x[1], reverse=True)[:5]
        if cid is not None
    ]

    if not top_cat_ids:
        return await list_deals(db, DealFilter())

    stmt = (
        select(Deal)
        .where(Deal.is_active.is_(True), Deal.category_id.in_(top_cat_ids))
        .order_by(Deal.discount_percent.desc().nulls_last())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    return [DealResponse.model_validate(d) for d in result.scalars().all()]


async def get_price_history(
    db: AsyncSession,
    user_id: uuid.UUID,
    product_name: str,
) -> list[PriceHistoryResponse]:
    stmt = (
        select(PriceHistory)
        .where(
            PriceHistory.user_id == user_id,
            PriceHistory.product_name.ilike(f"%{product_name}%"),
        )
        .order_by(PriceHistory.recorded_at.desc())
        .limit(100)
    )
    result = await db.execute(stmt)
    return [PriceHistoryResponse.model_validate(ph) for ph in result.scalars().all()]
