"""Category Pydantic schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from src.categories.models import CategoryType


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    parent_id: uuid.UUID | None = None
    icon: str | None = None
    color: str | None = None
    type: CategoryType
    is_system: bool = False


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    parent_id: uuid.UUID | None = None
    icon: str | None = None
    color: str | None = None
    type: CategoryType | None = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    name: str
    icon: str | None = None
    color: str | None = None
    type: CategoryType
    is_system: bool

    model_config = {"from_attributes": True}


class CategoryTree(CategoryResponse):
    children: list[CategoryTree] = []
