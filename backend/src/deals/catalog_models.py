"""Shared price catalogue: retail chains, their branches, products and price observations.

Prices come from users' confirmed receipts (and, optionally, a configured retailer
feed). Each observation belongs to one branch, so prices of the same chain are
kept apart per branch. Receipt observations are removed together with the
receipt line they came from.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


class RetailChain(Base):
    __tablename__ = "retail_chains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)


class StoreBranch(Base):
    __tablename__ = "store_branches"
    __table_args__ = (
        UniqueConstraint("chain_id", "branch_key", name="uq_store_branches_chain_branch"),
        CheckConstraint("lat IS NULL OR (lat BETWEEN -90 AND 90)", name="lat_range"),
        CheckConstraint("lon IS NULL OR (lon BETWEEN -180 AND 180)", name="lon_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("retail_chains.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    address: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    # Normalized "branch name|address"; an empty key is the chain's unknown branch.
    branch_key: Mapped[str] = mapped_column(String(420), nullable=False, default="")
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    # OpenStreetMap element ("node/123") once the branch is matched to the map.
    osm_ref: Mapped[str | None] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (Index("ix_products_barcode", "barcode"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # "gtin:<14 digits>" when a barcode is known, otherwise brand|name|variant|fat|unit|size.
    product_key: Mapped[str] = mapped_column(String(700), nullable=False, unique=True)
    barcode: Mapped[str | None] = mapped_column(String(14))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Case-folded "name brand variant" words, so search does not depend on the database collation.
    search_text: Mapped[str] = mapped_column(String(600), nullable=False, default="")
    brand: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    variant: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    fat_percent: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    package_size: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    # Normalized unit of package_size: l, kg or pc.
    package_unit: Mapped[str] = mapped_column(String(4), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)


class PriceObservation(Base):
    __tablename__ = "price_observations"
    __table_args__ = (
        Index("ix_price_observations_product_day", "product_id", "observed_on"),
        Index("ix_price_observations_branch_id", "branch_id"),
        CheckConstraint("source_kind IN ('receipt', 'catalog')", name="source_kind"),
        CheckConstraint("package_price IS NULL OR package_price > 0", name="package_price_positive"),
        CheckConstraint("unit_price IS NULL OR unit_price > 0", name="unit_price_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("store_branches.id", ondelete="CASCADE"), nullable=False
    )
    receipt_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("receipt_items.id", ondelete="CASCADE"), unique=True
    )
    observed_on: Mapped[date] = mapped_column(Date, nullable=False)
    package_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    unit: Mapped[str] = mapped_column(String(4), nullable=False, default="")
    condition: Mapped[str] = mapped_column(String(250), nullable=False, default="")
    source_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    source_name: Mapped[str] = mapped_column(String(160), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text)
    # Only a dated retailer source can confirm availability; receipts leave this null.
    available: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)


class ReceiptItem(Base):
    """One confirmed receipt line, normalized for queries and price comparison."""

    __tablename__ = "receipt_items"
    __table_args__ = (
        UniqueConstraint("transaction_id", "line_index", name="uq_receipt_items_transaction_line"),
        Index("ix_receipt_items_user_day", "user_id", "purchase_date"),
        Index("ix_receipt_items_product_id", "product_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    line_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # The product name exactly as printed on the receipt; never translated.
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("store_branches.id", ondelete="RESTRICT"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL")
    )
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    quantity_unit: Mapped[str] = mapped_column(String(4), nullable=False, default="")
    spend: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    package_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    promotion_condition: Mapped[str] = mapped_column(String(250), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)
