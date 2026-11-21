"""Budget Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from src.budgets.models import BudgetPeriod


class BudgetCreate(BaseModel):
    category_id: uuid.UUID | None = None
    limit_amount: Decimal = Field(gt=0)
    period: BudgetPeriod
    start_date: date
    end_date: date | None = None


class BudgetUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    limit_amount: Decimal | None = Field(default=None, gt=0)
    period: BudgetPeriod | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class BudgetResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category_id: uuid.UUID | None = None
    limit_amount: Decimal
    period: BudgetPeriod
    start_date: date
    end_date: date | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class BudgetStatus(BudgetResponse):
    spent: Decimal = Decimal("0")
    remaining: Decimal = Decimal("0")
    percentage: float = 0.0
