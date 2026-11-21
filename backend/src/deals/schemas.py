"""Deals Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class DealResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    store: str | None = None
    url: str | None = None
    original_price: Decimal | None = None
    discount_price: Decimal | None = None
    discount_percent: Decimal | None = None
    category_id: uuid.UUID | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    source: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DealFilter(BaseModel):
    store: str | None = None
    category_id: uuid.UUID | None = None
    min_discount: float | None = None
    is_active: bool = True


class PriceHistoryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    product_name: str
    store: str | None = None
    price: Decimal
    category_id: uuid.UUID | None = None
    recorded_at: datetime

    model_config = {"from_attributes": True}
