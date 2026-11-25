"""Shared fixtures for SmartBudget API tests.

The tests talk to the real FastAPI app over ASGI and to a real PostgreSQL
database. ``DATABASE_URL`` must point to a dedicated, disposable test database
whose schema was created with ``alembic upgrade head``. The suite refuses to
run against a database whose name does not contain ``test``.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import date

import httpx
import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.core.config import settings
from src.core.dependencies import get_db
from src.main import app

_db_name = make_url(settings.DATABASE_URL).database or ""
if "test" not in _db_name:
    raise RuntimeError(
        f"Refusing to run tests against database '{_db_name}'. "
        "Point DATABASE_URL to a dedicated test database."
    )

# NullPool keeps connections out of the pool, so each test's event loop gets
# fresh asyncpg connections.
test_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def _get_test_db() -> AsyncIterator[AsyncSession]:
    async with TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = _get_test_db


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def db() -> AsyncIterator[AsyncSession]:
    async with TestSession() as session:
        yield session


async def register_and_login(client: httpx.AsyncClient, name: str = "Tester") -> dict:
    """Create a fresh account and return auth headers plus profile data."""
    email = f"{name.lower()}-{uuid.uuid4().hex[:10]}@test.example"
    password = "Sup3r-secret-pass"
    res = await client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": name, "currency": "KZT"},
    )
    assert res.status_code == 201, res.text
    user = res.json()

    res = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    headers = {"Authorization": f"Bearer {res.json()['access_token']}"}
    return {"headers": headers, "user": user, "email": email, "password": password}


async def category_id(client: httpx.AsyncClient, headers: dict, name: str) -> str:
    res = await client.get("/api/categories/tree", headers=headers)
    assert res.status_code == 200, res.text
    for cat in res.json():
        if cat["name"] == name:
            return cat["id"]
    raise AssertionError(f"category {name} not found")


def month_range(today: date | None = None) -> tuple[str, str]:
    today = today or date.today()
    start = today.replace(day=1)
    if today.month == 12:
        nxt = today.replace(year=today.year + 1, month=1, day=1)
    else:
        nxt = today.replace(month=today.month + 1, day=1)
    end = date.fromordinal(nxt.toordinal() - 1)
    return start.isoformat(), end.isoformat()
