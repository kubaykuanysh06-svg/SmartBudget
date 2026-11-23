"""Auth business logic."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.categories.services import seed_default_categories
from src.core.exceptions import BadRequest, NotFound
from src.core.security import hash_password, verify_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    name: str,
    currency: str = "RUB",
) -> User:
    existing = await get_user_by_email(db, email)
    if existing:
        raise BadRequest("Email already registered")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        name=name,
        currency=currency,
    )
    db.add(user)
    await db.flush()
    await seed_default_categories(db, user.id)
    return user


async def authenticate(db: AsyncSession, *, email: str, password: str) -> User:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise BadRequest("Invalid email or password")
    return user
