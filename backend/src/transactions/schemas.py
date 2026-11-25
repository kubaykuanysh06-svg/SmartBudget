"""Transaction Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.categories.schemas import CategoryResponse
from src.transactions.models import Frequency, TransactionType

MAX_AMOUNT = Decimal("999999999999.99")


# ── Transaction ───────────────────────────────────────────


class TransactionCreate(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal = Field(gt=0, le=MAX_AMOUNT, decimal_places=2, allow_inf_nan=False)
    type: TransactionType
    description: str | None = None
    merchant: str | None = None
    transaction_date: date
    tags: list[str] | None = None
    receipt_url: str | None = None


class TransactionUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal | None = Field(
        default=None, gt=0, le=MAX_AMOUNT, decimal_places=2, allow_inf_nan=False
    )
    type: TransactionType | None = None
    description: str | None = None
    merchant: str | None = None
    transaction_date: date | None = None
    tags: list[str] | None = None
    receipt_url: str | None = None


class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category_id: uuid.UUID | None = None
    category: CategoryResponse | None = None
    amount: Decimal
    type: TransactionType
    description: str | None = None
    merchant: str | None = None
    transaction_date: date
    tags: list[str] | None = None
    receipt_url: str | None = None
    ai_metadata: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionFilter(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    category_id: uuid.UUID | None = None
    type: TransactionType | None = None
    merchant_search: str | None = None


class PaginatedTransactions(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    per_page: int


# ── Recurring Transaction ────────────────────────────────


class RecurringTransactionCreate(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal = Field(gt=0, le=MAX_AMOUNT, decimal_places=2, allow_inf_nan=False)
    type: TransactionType = TransactionType.expense
    description: str | None = None
    frequency: Frequency
    next_date: date


class RecurringTransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category_id: uuid.UUID | None = None
    amount: Decimal
    type: TransactionType
    description: str | None = None
    frequency: Frequency
    next_date: date
    is_active: bool

    model_config = {"from_attributes": True}
