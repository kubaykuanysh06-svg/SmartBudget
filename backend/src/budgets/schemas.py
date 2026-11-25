"""Budget Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from src.budgets.models import BudgetPeriod
from src.categories.schemas import CategoryResponse

MAX_AMOUNT = Decimal("999999999999.99")


class BudgetCreate(BaseModel):
    category_id: uuid.UUID | None = None
    limit_amount: Decimal = Field(
        gt=0, le=MAX_AMOUNT, decimal_places=2, allow_inf_nan=False
    )
    period: BudgetPeriod
    start_date: date
    end_date: date | None = None

    @model_validator(mode="after")
    def _check_dates(self) -> BudgetCreate:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class BudgetUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    limit_amount: Decimal | None = Field(
        default=None, gt=0, le=MAX_AMOUNT, decimal_places=2, allow_inf_nan=False
    )
    period: BudgetPeriod | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class BudgetResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category_id: uuid.UUID | None = None
    category: CategoryResponse | None = None
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
