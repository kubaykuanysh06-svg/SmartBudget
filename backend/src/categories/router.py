"""Category API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories import schemas, services
from src.core.dependencies import get_current_user, get_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/tree", response_model=list[schemas.CategoryTree])
async def get_tree(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    cats = await services.list_categories(db, current_user.id)
    return services.build_category_tree(cats)


@router.post("", response_model=schemas.CategoryResponse, status_code=201)
async def create_category(
    body: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.create_category(
        db, current_user.id, data=body.model_dump()
    )


@router.put("/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    body: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.update_category(
        db, category_id, current_user.id, data=body.model_dump(exclude_unset=True)
    )


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await services.delete_category(db, category_id, current_user.id)
