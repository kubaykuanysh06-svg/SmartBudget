"""Transaction business logic layer."""

from __future__ import annotations

import csv
import io
import uuid
from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BadRequest, NotFound
from src.transactions import repositories as repo
from src.transactions.models import RecurringTransaction, TransactionType
from src.transactions.schemas import (
    PaginatedTransactions,
    TransactionFilter,
    TransactionResponse,
)


async def create_transaction(
    db: AsyncSession, user_id: uuid.UUID, data: dict
) -> TransactionResponse:
    txn = await repo.create(db, user_id=user_id, data=data)
    return TransactionResponse.model_validate(txn)


async def get_transaction(
    db: AsyncSession, txn_id: uuid.UUID, user_id: uuid.UUID
) -> TransactionResponse:
    txn = await repo.get_by_id(db, txn_id, user_id)
    if not txn:
        raise NotFound("Transaction not found")
    return TransactionResponse.model_validate(txn)


async def update_transaction(
    db: AsyncSession, txn_id: uuid.UUID, user_id: uuid.UUID, data: dict
) -> TransactionResponse:
    txn = await repo.get_by_id(db, txn_id, user_id)
    if not txn:
        raise NotFound("Transaction not found")
    updated = await repo.update(db, txn, data)
    return TransactionResponse.model_validate(updated)


async def delete_transaction(
    db: AsyncSession, txn_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    txn = await repo.get_by_id(db, txn_id, user_id)
    if not txn:
        raise NotFound("Transaction not found")
    await repo.delete(db, txn)


async def list_transactions(
    db: AsyncSession,
    user_id: uuid.UUID,
    filters: TransactionFilter,
    page: int = 1,
    per_page: int = 20,
) -> PaginatedTransactions:
    items, total = await repo.list_filtered(
        db,
        user_id,
        date_from=filters.date_from,
        date_to=filters.date_to,
        category_id=filters.category_id,
        txn_type=filters.type,
        merchant_search=filters.merchant_search,
        page=page,
        per_page=per_page,
    )
    return PaginatedTransactions(
        items=[TransactionResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        per_page=per_page,
    )


async def import_csv(
    db: AsyncSession, user_id: uuid.UUID, file_content: str
) -> list[TransactionResponse]:
    """Parse a CSV (amount, type, description, merchant, date) and bulk-create."""
    reader = csv.DictReader(io.StringIO(file_content))
    created: list[TransactionResponse] = []
    for row in reader:
        try:
            amount = Decimal(row["amount"])
        except (InvalidOperation, KeyError):
            raise BadRequest(f"Invalid amount in row: {row}")

        txn_type = row.get("type", "expense")
        if txn_type not in TransactionType.__members__:
            raise BadRequest(f"Invalid type '{txn_type}'")

        txn_date = row.get("date") or row.get("transaction_date")
        if not txn_date:
            raise BadRequest("Missing date column")

        data = {
            "amount": amount,
            "type": TransactionType(txn_type),
            "description": row.get("description"),
            "merchant": row.get("merchant"),
            "transaction_date": date.fromisoformat(txn_date),
        }
        txn = await repo.create(db, user_id=user_id, data=data)
        created.append(TransactionResponse.model_validate(txn))
    return created
