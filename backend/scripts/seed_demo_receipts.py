"""Seed a local demo account with receipts for manual UI testing.

Run inside the backend container against a development database only:
    docker compose exec backend python scripts/seed_demo_receipts.py
Prints the generated account email; the password is DEMO_PASSWORD below.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone

import httpx
from jose import jwt

from src.core.config import settings
from src.main import app

DEMO_PASSWORD = "Demo-receipts-2026"


def token(user_id: str) -> str:
    return jwt.encode(
        {"sub": user_id, "type": "receipt-upload", "file_hash": uuid.uuid4().hex, "identity_hash": None,
         "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        settings.SECRET_KEY, algorithm=settings.ALGORITHM,
    )


def milk(size: str, price: str, quantity: str = "1", **extra) -> dict:
    return {"name": f"Молоко Lactel 2,5% {size} л", "brand": "Lactel", "variant": "пастерленген",
            "fat_percent": "2.5", "package_size": size, "package_unit": "л", "quantity": quantity,
            "unit": "шт", "unit_price": price, "line_total": str(float(price) * float(quantity)),
            "discount": "0", **extra}


async def main() -> None:
    if settings.APP_ENV == "production":
        raise SystemExit("Refusing to seed a production environment")
    today = date.today()
    email = f"demo-{uuid.uuid4().hex[:8]}@example.com"
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://seed") as client:
        user = (await client.post("/api/auth/register", json={
            "email": email, "password": DEMO_PASSWORD, "name": "Demo", "currency": "KZT"})).json()
        login = (await client.post("/api/auth/login", json={"email": email, "password": DEMO_PASSWORD})).json()
        headers = {"Authorization": f"Bearer {login['access_token']}"}
        categories = (await client.get("/api/categories/tree", headers=headers)).json()
        groceries = next((c["id"] for c in categories if c["name"] == "Groceries"), None)
        receipts = [
            ("Magnum", "№12", "Абай даңғылы 10", today - timedelta(days=35), [milk("1", "560", "2")]),
            ("Magnum", "№12", "Абай даңғылы 10", today.replace(day=1), [
                milk("0.9", "540"),
                {"name": "Нан бородинский", "quantity": "1", "unit": "шт", "unit_price": "250",
                 "line_total": "250", "discount": "0"},
            ]),
            ("Magnum", "№7", "Төле би 4", today, [milk("1", "600", "3")]),
            ("Small", "", "Сейфуллин 5", today, [
                milk("1", "580"),
                milk("1", "590", discount="50", line_total_is_net=False, promotion_condition="Small Club картасымен"),
                {**milk("1", "520"), "name": "Молоко Lactel 3,2% 1 л", "fat_percent": "3.2"},
            ]),
        ]
        for index, (merchant, branch, address, day, items) in enumerate(receipts):
            for item in items:
                item["category_id"] = groceries
            paid = sum(float(i["line_total"]) - float(i.get("discount") or 0) for i in items)
            res = await client.post("/api/receipts", headers=headers, json={
                "merchant": merchant, "branch": branch, "branch_address": address,
                "purchase_date": day.isoformat(), "receipt_number": f"demo-{index}",
                "paid": f"{paid:.2f}", "items": items, "upload_token": token(user["id"]),
            })
            res.raise_for_status()
    print(email)


asyncio.run(main())
