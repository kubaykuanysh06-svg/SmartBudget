"""Transaction repository — CRUD, filtered list, aggregations."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Numeric, cast, column, func, select, true, union_all
from sqlalchemy.dialects.postgresql import JSONB, UUID, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.transactions.models import Transaction, TransactionType


async def create(db: AsyncSession, *, user_id: uuid.UUID, data: dict) -> Transaction:
    txn = Transaction(user_id=user_id, **data)
    db.add(txn)
    await db.flush()
    await db.refresh(txn, attribute_names=["category"])
    return txn


async def create_once(
    db: AsyncSession, *, user_id: uuid.UUID, txn_id: uuid.UUID, data: dict
) -> Transaction | None:
    statement = (
        insert(Transaction)
        .values(id=txn_id, user_id=user_id, **data)
        .on_conflict_do_nothing(index_elements=[Transaction.id])
    )
    await db.execute(statement)
    return await get_by_id(db, txn_id, user_id)


async def get_by_id(
    db: AsyncSession, txn_id: uuid.UUID, user_id: uuid.UUID, *, for_update: bool = False
) -> Transaction | None:
    statement = (
        select(Transaction)
        .options(selectinload(Transaction.category))
        .where(Transaction.id == txn_id, Transaction.user_id == user_id)
    )
    if for_update:
        statement = statement.with_for_update()
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def update(
    db: AsyncSession, txn: Transaction, data: dict
) -> Transaction:
    nullable_fields = {"category_id", "description", "merchant", "tags", "receipt_url"}
    for k, v in data.items():
        if v is not None or k in nullable_fields:
            setattr(txn, k, v)
    await db.flush()
    await db.refresh(txn, attribute_names=["category"])
    return txn


async def delete(db: AsyncSession, txn: Transaction) -> None:
    await db.delete(txn)
    await db.flush()


async def list_filtered(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    category_id: uuid.UUID | None = None,
    txn_type: TransactionType | None = None,
    merchant_search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Transaction], int]:
    stmt = (
        select(Transaction)
        .options(selectinload(Transaction.category))
        .where(Transaction.user_id == user_id)
    )
    count_stmt = select(func.count(Transaction.id)).where(
        Transaction.user_id == user_id
    )

    if date_from:
        stmt = stmt.where(Transaction.transaction_date >= date_from)
        count_stmt = count_stmt.where(Transaction.transaction_date >= date_from)
    if date_to:
        stmt = stmt.where(Transaction.transaction_date <= date_to)
        count_stmt = count_stmt.where(Transaction.transaction_date <= date_to)
    if category_id:
        stmt = stmt.where(Transaction.category_id == category_id)
        count_stmt = count_stmt.where(Transaction.category_id == category_id)
    if txn_type:
        stmt = stmt.where(Transaction.type == txn_type)
        count_stmt = count_stmt.where(Transaction.type == txn_type)
    if merchant_search:
        pattern = f"%{merchant_search}%"
        stmt = stmt.where(Transaction.merchant.ilike(pattern))
        count_stmt = count_stmt.where(Transaction.merchant.ilike(pattern))

    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        stmt.order_by(Transaction.transaction_date.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all()), int(total)


async def sum_by_type(
    db: AsyncSession,
    user_id: uuid.UUID,
    txn_type: TransactionType,
    date_from: date | None = None,
    date_to: date | None = None,
) -> Decimal:
    stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == user_id,
        Transaction.type == txn_type,
    )
    if date_from:
        stmt = stmt.where(Transaction.transaction_date >= date_from)
    if date_to:
        stmt = stmt.where(Transaction.transaction_date <= date_to)

    result = await db.execute(stmt)
    return Decimal(str(result.scalar()))


async def sum_by_category(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    txn_type: TransactionType | None = None,
) -> list[tuple[uuid.UUID | None, Decimal]]:
    rows = category_amount_rows(user_id, date_from, date_to, txn_type)
    stmt = select(rows.c.category_id, func.sum(rows.c.amount)).group_by(rows.c.category_id)
    result = await db.execute(stmt)
    return [(row[0], Decimal(str(row[1]))) for row in result.all()]


async def monthly_totals(
    db: AsyncSession,
    user_id: uuid.UUID,
    txn_type: TransactionType,
    *,
    months: int = 12,
) -> list[tuple[str, Decimal]]:
    """Return (YYYY-MM, total) for the most recent N months in ascending order."""
    month_col = func.to_char(Transaction.transaction_date, "YYYY-MM").label("month")
    stmt = (
        select(
            month_col,
            func.sum(Transaction.amount),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.type == txn_type,
        )
        .group_by(month_col)
        .order_by(month_col.desc())
        .limit(months)
    )
    result = await db.execute(stmt)
    rows = [(row[0], Decimal(str(row[1]))) for row in result.all()]
    rows.reverse()
    return rows


async def spending_by_category_in_range(
    db: AsyncSession,
    user_id: uuid.UUID,
    category_id: uuid.UUID,
    date_from: date,
    date_to: date,
) -> Decimal:
    rows = category_amount_rows(user_id, date_from, date_to, TransactionType.expense)
    stmt = select(func.coalesce(func.sum(rows.c.amount), 0)).where(
        rows.c.category_id == category_id,
    )
    result = await db.execute(stmt)
    return Decimal(str(result.scalar()))


async def daily_expenses_in_range(
    db: AsyncSession,
    user_id: uuid.UUID,
    date_from: date,
    date_to: date,
    *,
    only_receipts: bool = False,
) -> list[tuple[uuid.UUID | None, date, Decimal]]:
    """Aggregate expense totals grouped by (category_id, transaction_date) in one query."""
    rows = category_amount_rows(
        user_id, date_from, date_to, TransactionType.expense, only_receipts=only_receipts
    )
    stmt = select(rows.c.category_id, rows.c.transaction_date, func.sum(rows.c.amount)).group_by(
        rows.c.category_id, rows.c.transaction_date
    )
    result = await db.execute(stmt)
    return [(row[0], row[1], Decimal(str(row[2]))) for row in result.all()]


def category_amount_rows(
    user_id: uuid.UUID,
    date_from: date | None = None,
    date_to: date | None = None,
    txn_type: TransactionType | None = None,
    *,
    only_receipts: bool = False,
):
    """Use each receipt's allocated items in place of its parent transaction amount."""
    filters = [Transaction.user_id == user_id]
    if date_from:
        filters.append(Transaction.transaction_date >= date_from)
    if date_to:
        filters.append(Transaction.transaction_date <= date_to)
    if txn_type:
        filters.append(Transaction.type == txn_type)

    receipt = Transaction.ai_metadata["receipt"]
    items = (
        func.jsonb_array_elements(receipt["items"])
        .table_valued(column("item", JSONB))
        .render_derived(name="receipt_item")
        .lateral()
    )
    allocated = (
        select(
            cast(items.c.item["category_id"].astext, UUID).label("category_id"),
            Transaction.transaction_date,
            cast(items.c.item["allocated_amount"].astext, Numeric(14, 2)).label("amount"),
        )
        .select_from(Transaction)
        .join(items, true())
        .where(*filters, receipt.is_not(None))
    )
    if only_receipts:
        return allocated.subquery()
    ordinary = select(Transaction.category_id, Transaction.transaction_date, Transaction.amount).where(
        *filters, receipt.is_(None)
    )
    return union_all(ordinary, allocated).subquery()
