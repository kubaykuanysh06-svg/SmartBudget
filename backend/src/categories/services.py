"""Category business logic, tree builder, and default seed."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.models import Category, CategoryType
from src.categories.schemas import CategoryResponse, CategoryTree
from src.core.exceptions import BadRequest, Forbidden, NotFound

# ── Default categories seeded for new users ───────────────

DEFAULT_CATEGORIES: list[dict] = [
    {"name": "Salary", "icon": "💰", "color": "#4CAF50", "type": CategoryType.income},
    {"name": "Freelance", "icon": "💻", "color": "#8BC34A", "type": CategoryType.income},
    {"name": "Investments", "icon": "📈", "color": "#00BCD4", "type": CategoryType.income},
    {"name": "Groceries", "icon": "🛒", "color": "#FF9800", "type": CategoryType.expense},
    {"name": "Transport", "icon": "🚌", "color": "#2196F3", "type": CategoryType.expense},
    {"name": "Utilities", "icon": "💡", "color": "#9C27B0", "type": CategoryType.expense},
    {"name": "Entertainment", "icon": "🎬", "color": "#E91E63", "type": CategoryType.expense},
    {"name": "Health", "icon": "🏥", "color": "#F44336", "type": CategoryType.expense},
    {"name": "Dining", "icon": "🍽️", "color": "#FF5722", "type": CategoryType.expense},
    {"name": "Shopping", "icon": "🛍️", "color": "#673AB7", "type": CategoryType.expense},
    {"name": "Education", "icon": "📚", "color": "#3F51B5", "type": CategoryType.expense},
    {"name": "Other", "icon": "📦", "color": "#607D8B", "type": CategoryType.expense},
]


async def seed_default_categories(db: AsyncSession, user_id: uuid.UUID) -> list[Category]:
    """Create default categories for a newly registered user."""
    categories = [
        Category(user_id=user_id, is_system=True, **cat) for cat in DEFAULT_CATEGORIES
    ]
    db.add_all(categories)
    await db.flush()
    return categories


# ── CRUD ──────────────────────────────────────────────────


async def list_categories(db: AsyncSession, user_id: uuid.UUID) -> list[Category]:
    result = await db.execute(
        select(Category).where(Category.user_id == user_id).order_by(Category.name)
    )
    return list(result.scalars().all())


async def get_category(
    db: AsyncSession, category_id: uuid.UUID, user_id: uuid.UUID
) -> Category:
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise NotFound("Category not found")
    return cat


async def create_category(
    db: AsyncSession, user_id: uuid.UUID, *, data: dict
) -> Category:
    payload = {k: v for k, v in data.items() if k != "is_system"}
    parent_id = payload.get("parent_id")
    if parent_id is not None:
        await get_category(db, parent_id, user_id)
    cat = Category(user_id=user_id, is_system=False, **payload)
    db.add(cat)
    await db.flush()
    return cat


async def update_category(
    db: AsyncSession,
    category_id: uuid.UUID,
    user_id: uuid.UUID,
    *,
    data: dict,
) -> Category:
    cat = await get_category(db, category_id, user_id)
    if cat.is_system:
        raise Forbidden("Cannot modify system categories")
    if "parent_id" in data and data["parent_id"] is not None:
        if data["parent_id"] == category_id:
            raise BadRequest("Category cannot be its own parent")
        await get_category(db, data["parent_id"], user_id)
    nullable_fields = {"parent_id", "icon", "color"}
    for k, v in data.items():
        if k == "is_system":
            continue
        if v is not None or k in nullable_fields:
            setattr(cat, k, v)
    await db.flush()
    return cat


async def delete_category(
    db: AsyncSession, category_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    cat = await get_category(db, category_id, user_id)
    if cat.is_system:
        raise Forbidden("Cannot delete system categories")
    await db.delete(cat)
    await db.flush()


# ── Tree builder ──────────────────────────────────────────


def build_category_tree(categories: list[Category]) -> list[CategoryTree]:
    """Build a nested tree from a flat list of categories."""
    nodes: dict[uuid.UUID, CategoryTree] = {}
    for cat in categories:
        category = CategoryResponse.model_validate(cat)
        nodes[cat.id] = CategoryTree(**category.model_dump())

    roots: list[CategoryTree] = []
    for cat in categories:
        node = nodes[cat.id]
        if cat.parent_id and cat.parent_id in nodes:
            nodes[cat.parent_id].children.append(node)
        else:
            roots.append(node)
    return roots
