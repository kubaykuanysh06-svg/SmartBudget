"""Backfill normalized receipt_items and price_observations from stored receipts.

Run inside the backend container after upgrading to revision 0004:
    docker compose exec backend python scripts/backfill_receipt_items.py
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from src.ai import models as ai_models  # noqa: F401
from src.auth import models as auth_models  # noqa: F401
from src.budgets import models as budget_models  # noqa: F401
from src.categories import models as category_models  # noqa: F401
from src.core.database import async_session
from src.deals.catalog import sync_receipt
from src.deals.catalog_models import ReceiptItem
from src.deals import models as deals_models  # noqa: F401
from src.transactions.models import Transaction, TransactionType


async def backfill() -> tuple[int, int]:
    receipts_count = 0
    lines_count = 0
    async with async_session() as db:
        rows = (
            await db.scalars(
                select(Transaction)
                .where(
                    Transaction.type == TransactionType.expense,
                    Transaction.ai_metadata["receipt"].is_not(None),
                    ~select(ReceiptItem.id).where(ReceiptItem.transaction_id == Transaction.id).exists(),
                )
                .order_by(Transaction.transaction_date, Transaction.created_at)
                .with_for_update()
            )
        ).all()
        for txn in rows:
            lines_count += await sync_receipt(db, txn)
            receipts_count += 1
        await db.commit()
    return receipts_count, lines_count


async def main() -> None:
    receipts_count, lines_count = await backfill()
    print(f"Synced {receipts_count} receipts ({lines_count} lines).")


if __name__ == "__main__":
    asyncio.run(main())
