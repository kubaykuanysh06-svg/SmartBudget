"""Keep recorded prices in step with confirmed receipts."""

from __future__ import annotations

import uuid
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.deals.catalog_models import (
    PriceObservation,
    Product,
    ReceiptItem,
    RetailChain,
    StoreBranch,
)
from src.transactions.models import Transaction
from src.transactions.receipt_insights import ZERO, lines_for, normalized, number
from src.transactions.receipt_insights import Product as ProductIdentity
from src.transactions.schemas import MAX_AMOUNT

CENT = Decimal("0.01")
RECEIPT_SOURCE = "receipt"


def branch_key(branch: str, address: str) -> str:
    return f"{normalized(branch)}|{normalized(address)}"[:420]


def identity_from_row(row: Product) -> ProductIdentity:
    """Rebuild the matching identity of a stored product."""
    fat = format(row.fat_percent.normalize(), "f") if row.fat_percent is not None else ""
    size = row.package_size.normalize() if row.package_size is not None else ZERO
    return ProductIdentity(
        row.name, row.brand, row.barcode or "", row.variant, fat, size, row.package_unit
    )


async def chain_branch(db: AsyncSession, merchant: str, branch: str, address: str) -> StoreBranch:
    name = merchant.strip()[:255] or "?"
    name_key = normalized(name)[:255] or "?"
    await db.execute(
        insert(RetailChain)
        .values(id=uuid.uuid4(), name=name, name_key=name_key)
        .on_conflict_do_nothing(index_elements=[RetailChain.name_key])
    )
    chain_id = await db.scalar(select(RetailChain.id).where(RetailChain.name_key == name_key))
    key = branch_key(branch, address)
    await db.execute(
        insert(StoreBranch)
        .values(
            id=uuid.uuid4(),
            chain_id=chain_id,
            name=branch.strip()[:160],
            address=address.strip()[:255],
            branch_key=key,
        )
        .on_conflict_do_nothing(constraint="uq_store_branches_chain_branch")
    )
    return (
        await db.scalars(
            select(StoreBranch).where(
                StoreBranch.chain_id == chain_id, StoreBranch.branch_key == key
            )
        )
    ).one()


async def ensure_products(
    db: AsyncSession, identities: list[ProductIdentity]
) -> dict[str, uuid.UUID]:
    """Upsert all distinct products of a receipt in one batch and return key -> id."""
    unique_by_key: dict[str, ProductIdentity] = {}
    for identity in identities:
        unique_by_key.setdefault(identity.key[:700], identity)
    if not unique_by_key:
        return {}

    payload = [
        {
            "id": uuid.uuid4(),
            "product_key": key,
            "barcode": identity.barcode or None,
            "name": identity.name[:255] or "?",
            "search_text": normalized(
                f"{identity.name} {identity.brand} {identity.variant}"
            )[:600],
            "brand": identity.brand[:120],
            "variant": identity.variant[:120],
            "fat_percent": number(identity.fat_percent) if identity.fat_percent else None,
            "package_size": identity.package_size or None,
            "package_unit": identity.unit,
        }
        for key, identity in sorted(unique_by_key.items())
    ]
    await db.execute(
        insert(Product).values(payload).on_conflict_do_nothing(index_elements=[Product.product_key])
    )
    rows = (
        await db.execute(
            select(Product.product_key, Product.id).where(
                Product.product_key.in_(list(unique_by_key))
            )
        )
    ).all()
    return {product_key: product_id for product_key, product_id in rows}


def _price(value: Decimal | None) -> Decimal | None:
    if value is None or value <= 0 or value > MAX_AMOUNT:
        return None
    return value.quantize(CENT, rounding=ROUND_HALF_UP) or None


async def sync_receipt(db: AsyncSession, transaction: Transaction) -> int:
    """Replace the receipt lines and price observations of one receipt transaction."""
    await db.execute(delete(ReceiptItem).where(ReceiptItem.transaction_id == transaction.id))
    lines = lines_for(transaction)
    if not lines:
        return 0

    receipt = (transaction.ai_metadata or {}).get("receipt") or {}
    items = receipt.get("items") or []
    first = lines[0]
    branch = await chain_branch(db, first.merchant, first.branch, first.address)
    product_ids = await ensure_products(db, [line.product for line in lines])

    created_items: list[tuple[ReceiptItem, str]] = []
    for line in lines:
        product_id = product_ids[line.product.key[:700]]
        raw = items[line.index] if line.index < len(items) else {}
        category_id = line.category_id
        try:
            category = uuid.UUID(str(category_id)) if category_id else None
        except ValueError:
            category = None
        item = ReceiptItem(
            id=uuid.uuid4(),
            transaction_id=transaction.id,
            user_id=transaction.user_id,
            line_index=line.index,
            original_name=str(raw.get("name") or line.product.name)[:255],
            product_id=product_id,
            branch_id=branch.id,
            category_id=category,
            purchase_date=line.day,
            quantity=line.quantity or number(raw.get("quantity")) or None,
            quantity_unit=line.quantity_unit,
            spend=line.spend.quantize(CENT),
            discount=line.discount.quantize(CENT),
            package_price=_price(line.package_price()),
            unit_price=_price(line.unit_price()),
            promotion_condition=line.condition[:250],
        )
        created_items.append((item, line.product.unit))

    db.add_all([item for item, _ in created_items])
    await db.flush()

    observations = [
        PriceObservation(
            product_id=item.product_id,
            branch_id=branch.id,
            receipt_item_id=item.id,
            observed_on=item.purchase_date,
            package_price=item.package_price,
            unit_price=item.unit_price,
            unit=unit,
            condition=item.promotion_condition,
            source_kind=RECEIPT_SOURCE,
            source_name="receipt",
        )
        for item, unit in created_items
        if item.package_price is not None or item.unit_price is not None
    ]
    if observations:
        db.add_all(observations)
        await db.flush()
    return len(lines)
