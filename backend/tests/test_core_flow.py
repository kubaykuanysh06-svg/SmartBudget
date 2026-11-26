"""End-to-end API scenarios for the core finance features."""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from src.transactions.models import Transaction
from tests.conftest import category_id, month_range, register_and_login


async def _count_txns(db, user_id: str) -> int:
    return (
        await db.execute(
            select(func.count(Transaction.id)).where(Transaction.user_id == uuid.UUID(user_id))
        )
    ).scalar_one()


async def test_register_login_and_profile(client):
    acc = await register_and_login(client, "Alice")
    res = await client.get("/api/auth/me", headers=acc["headers"])
    assert res.status_code == 200
    assert res.json()["email"] == acc["email"]
    assert res.json()["currency"] == "KZT"

    bad = await client.post(
        "/api/auth/login", json={"email": acc["email"], "password": "wrong-password"}
    )
    assert bad.status_code == 400

    anon = await client.get("/api/transactions")
    assert anon.status_code == 401


async def test_income_expense_balance_and_budget(client, db):
    acc = await register_and_login(client, "Balance")
    h = acc["headers"]
    today = date.today().isoformat()
    salary = await category_id(client, h, "Salary")
    groceries = await category_id(client, h, "Groceries")

    r1 = await client.post(
        "/api/transactions",
        headers=h,
        json={"amount": 50000, "type": "income", "description": "Зарплата",
              "category_id": salary, "transaction_date": today},
    )
    r2 = await client.post(
        "/api/transactions",
        headers=h,
        json={"amount": 8000, "type": "expense", "description": "Продукты",
              "merchant": "Magnum", "category_id": groceries, "transaction_date": today},
    )
    assert r1.status_code == 201, r1.text
    assert r2.status_code == 201, r2.text

    # Persisted rows: owner, category, amount and date are stored exactly.
    rows = (
        await db.execute(
            select(Transaction).where(Transaction.user_id == uuid.UUID(acc["user"]["id"]))
        )
    ).scalars().all()
    by_type = {r.type.value: r for r in rows}
    assert len(rows) == 2
    assert by_type["income"].amount == Decimal("50000.00")
    assert str(by_type["income"].category_id) == salary
    assert by_type["expense"].amount == Decimal("8000.00")
    assert str(by_type["expense"].category_id) == groceries
    assert by_type["expense"].merchant == "Magnum"
    assert all(r.transaction_date.isoformat() == today for r in rows)

    # A fresh read (what a page refresh does) returns both records.
    listed = await client.get("/api/transactions", headers=h)
    assert listed.json()["total"] == 2

    start, end = month_range()
    summary = (
        await client.get(
            "/api/analytics/summary", headers=h, params={"date_from": start, "date_to": end}
        )
    ).json()
    assert Decimal(summary["total_income"]) == Decimal("50000")
    assert Decimal(summary["total_expense"]) == Decimal("8000")
    assert Decimal(summary["net"]) == Decimal("42000")

    breakdown = (await client.get("/api/analytics/by-category", headers=h)).json()
    assert [(b["category_name"], Decimal(b["total"])) for b in breakdown] == [
        ("Groceries", Decimal("8000"))
    ]

    b = await client.post(
        "/api/budgets",
        headers=h,
        json={"limit_amount": 20000, "period": "monthly", "start_date": today},
    )
    assert b.status_code == 201, b.text
    status = (await client.get("/api/budgets/status", headers=h)).json()
    assert len(status) == 1
    assert Decimal(status[0]["spent"]) == Decimal("8000")
    assert Decimal(status[0]["remaining"]) == Decimal("12000")
    assert status[0]["percentage"] == 40.0


async def test_accounts_are_isolated(client, db):
    a = await register_and_login(client, "OwnerA")
    b = await register_and_login(client, "OwnerB")
    today = date.today().isoformat()
    a_groceries = await category_id(client, a["headers"], "Groceries")

    created = await client.post(
        "/api/transactions",
        headers=a["headers"],
        json={"amount": 8000, "type": "expense", "description": "A only",
              "category_id": a_groceries, "transaction_date": today},
    )
    assert created.status_code == 201
    txn_id = created.json()["id"]
    await client.post(
        "/api/budgets",
        headers=a["headers"],
        json={"limit_amount": 20000, "period": "monthly", "start_date": today},
    )

    hb = b["headers"]
    assert (await client.get("/api/transactions", headers=hb)).json()["total"] == 0
    summary = (await client.get("/api/analytics/summary", headers=hb)).json()
    assert Decimal(summary["total_expense"]) == 0
    assert Decimal(summary["net"]) == 0
    assert (await client.get("/api/analytics/by-category", headers=hb)).json() == []
    assert (await client.get("/api/analytics/trends", headers=hb)).json() == []
    assert (await client.get("/api/budgets/status", headers=hb)).json() == []
    assert (await client.get(f"/api/transactions/{txn_id}", headers=hb)).status_code == 404
    assert (
        await client.put(f"/api/transactions/{txn_id}", headers=hb, json={"amount": 1})
    ).status_code == 404
    assert (await client.delete(f"/api/transactions/{txn_id}", headers=hb)).status_code == 404

    # B must not be able to attach A's category to its own records.
    foreign = await client.post(
        "/api/transactions",
        headers=hb,
        json={"amount": 100, "type": "expense", "description": "foreign cat",
              "category_id": a_groceries, "transaction_date": today},
    )
    assert foreign.status_code in (400, 404, 422), foreign.text
    foreign_budget = await client.post(
        "/api/budgets",
        headers=hb,
        json={"limit_amount": 100, "period": "monthly", "start_date": today,
              "category_id": a_groceries},
    )
    assert foreign_budget.status_code in (400, 404, 422), foreign_budget.text
    assert await _count_txns(db, b["user"]["id"]) == 0

    # A's data is untouched by B's attempts.
    a_status = (await client.get("/api/budgets/status", headers=a["headers"])).json()
    assert Decimal(a_status[0]["spent"]) == Decimal("8000")
    assert (await client.get(f"/api/transactions/{txn_id}", headers=a["headers"])).status_code == 200


@pytest.mark.parametrize(
    "amount",
    [0, -500, "abc", "", None, "NaN", "Infinity", 1e20, "100000000000000", "10.555"],
)
async def test_invalid_amount_is_rejected_without_writing(client, db, amount):
    acc = await register_and_login(client, "Invalid")
    res = await client.post(
        "/api/transactions",
        headers=acc["headers"],
        json={"amount": amount, "type": "expense", "description": "bad",
              "transaction_date": date.today().isoformat()},
    )
    assert res.status_code == 422, (amount, res.status_code, res.text)
    detail = res.json()["detail"]
    assert isinstance(detail, list) and detail
    assert detail[0]["loc"][-1] == "amount"
    assert detail[0]["msg"]
    assert await _count_txns(db, acc["user"]["id"]) == 0


async def test_largest_valid_amount_is_stored(client, db):
    acc = await register_and_login(client, "Big")
    res = await client.post(
        "/api/transactions",
        headers=acc["headers"],
        json={"amount": "999999999999.99", "type": "income", "description": "max",
              "transaction_date": date.today().isoformat()},
    )
    assert res.status_code == 201, res.text
    assert await _count_txns(db, acc["user"]["id"]) == 1


async def test_csv_import_validates_rows(client, db):
    acc = await register_and_login(client, "Csv")
    h = acc["headers"]
    today = date.today().isoformat()
    for body in (
        f"amount,type,description,date\n-100,expense,neg,{today}\n",
        "amount,type,description,date\n100,expense,bad date,26.11.2026\n",
        f"amount,type,description,date\n0,expense,zero,{today}\n",
    ):
        res = await client.post(
            "/api/transactions/import", headers=h,
            files={"file": ("t.csv", body.encode(), "text/csv")},
        )
        assert res.status_code == 400, (body, res.status_code, res.text)
    assert await _count_txns(db, acc["user"]["id"]) == 0

    ok = await client.post(
        "/api/transactions/import", headers=h,
        files={"file": ("t.csv", f"amount,type,description,date\n150.50,expense,ok,{today}\n".encode(), "text/csv")},
    )
    assert ok.status_code == 200, ok.text
    assert await _count_txns(db, acc["user"]["id"]) == 1


async def test_trends_return_most_recent_months(client):
    acc = await register_and_login(client, "Trend")
    h = acc["headers"]
    today = date.today().replace(day=1)
    months = []
    y, m = today.year, today.month
    for _ in range(14):
        months.append(date(y, m, 1))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    for d in months:
        res = await client.post(
            "/api/transactions", headers=h,
            json={"amount": 100, "type": "expense", "description": "m",
                  "transaction_date": d.isoformat()},
        )
        assert res.status_code == 201

    points = (await client.get("/api/analytics/trends", headers=h, params={"months": 12})).json()
    assert len(points) == 12
    assert points[-1]["month"] == today.strftime("%Y-%m")
    assert points[0]["month"] == months[11].strftime("%Y-%m")


async def test_client_cannot_create_system_category(client):
    acc = await register_and_login(client, "Cat")
    res = await client.post(
        "/api/categories", headers=acc["headers"],
        json={"name": "Mine", "type": "expense", "is_system": True},
    )
    assert res.status_code == 201
    assert res.json()["is_system"] is False
    deleted = await client.delete(f"/api/categories/{res.json()['id']}", headers=acc["headers"])
    assert deleted.status_code == 204


async def test_ai_without_key_does_not_break_finance(client, monkeypatch):
    from src.core.config import settings

    acc = await register_and_login(client, "NoAi")
    h = acc["headers"]

    for placeholder in ("", "your-gemini-api-key"):
        monkeypatch.setattr(settings, "GEMINI_API_KEY", placeholder)
        res = await client.post("/api/ai/chat", headers=h, json={"message": "Как сэкономить?"})
        assert res.status_code == 503
        assert "Gemini" in res.json()["detail"]

        price_res = await client.post(
            "/api/ai/analyze-price",
            headers=h,
            json={"description": "Кофе Lavazza 1кг", "amount": 9500},
        )
        assert price_res.status_code == 503

    assert (await client.get("/api/ai/insights", headers=h)).status_code == 200

    created = await client.post(
        "/api/transactions", headers=h,
        json={"amount": 1000, "type": "expense", "description": "ok",
              "transaction_date": date.today().isoformat()},
    )
    assert created.status_code == 201
    assert (await client.get("/api/analytics/summary", headers=h)).status_code == 200


async def test_category_objects_embedded_and_profile_patch(client):
    acc = await register_and_login(client, "Rich")
    h = acc["headers"]
    today = date.today().isoformat()
    groceries = await category_id(client, h, "Groceries")

    txn = await client.post(
        "/api/transactions",
        headers=h,
        json={"amount": 4500, "type": "expense", "description": "Хлеб и молоко",
              "category_id": groceries, "transaction_date": today},
    )
    assert txn.status_code == 201
    assert txn.json()["category"]["name"] == "Groceries"

    b = await client.post(
        "/api/budgets",
        headers=h,
        json={"category_id": groceries, "limit_amount": 15000, "period": "monthly", "start_date": today},
    )
    assert b.status_code == 201
    statuses = (await client.get("/api/budgets/status", headers=h)).json()
    assert statuses[0]["category"]["name"] == "Groceries"
    assert Decimal(statuses[0]["spent"]) == Decimal("4500")
    assert Decimal(statuses[0]["remaining"]) == Decimal("10500")
    assert statuses[0]["percentage"] == 30.0

    patched = await client.patch(
        "/api/auth/me", headers=h, json={"name": "Rich Updated", "currency": "usd"}
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "Rich Updated"
    assert patched.json()["currency"] == "USD"


async def test_budget_counts_only_inside_its_dates(client):
    acc = await register_and_login(client, "Dates")
    h = acc["headers"]
    today = date.today()
    res = await client.post(
        "/api/transactions", headers=h,
        json={"amount": 8000, "type": "expense", "description": "x",
              "transaction_date": today.isoformat()},
    )
    assert res.status_code == 201
    first_of_month = today.replace(day=1)
    next_month = (first_of_month + timedelta(days=32)).replace(day=1)
    ended = first_of_month - timedelta(days=1)
    for body in (
        {"start_date": next_month.isoformat()},  # not started yet
        {"start_date": ended.replace(day=1).isoformat(), "end_date": ended.isoformat()},  # ended
        {"start_date": today.isoformat()},  # current
    ):
        r = await client.post(
            "/api/budgets", headers=h,
            json={"limit_amount": 20000, "period": "monthly", **body},
        )
        assert r.status_code == 201, r.text
    spent = {
        b["start_date"]: Decimal(b["spent"])
        for b in (await client.get("/api/budgets/status", headers=h)).json()
    }
    assert spent[next_month.isoformat()] == 0
    assert spent[ended.replace(day=1).isoformat()] == 0
    assert spent[today.isoformat()] == Decimal("8000")


async def test_category_type_must_match_transaction_type(client, db):
    acc = await register_and_login(client, "Types")
    h = acc["headers"]
    today = date.today().isoformat()
    groceries = await category_id(client, h, "Groceries")
    salary = await category_id(client, h, "Salary")

    wrong = await client.post(
        "/api/transactions", headers=h,
        json={"amount": 5000, "type": "income", "category_id": groceries,
              "description": "wrong", "transaction_date": today},
    )
    assert wrong.status_code == 400, wrong.text
    assert await _count_txns(db, acc["user"]["id"]) == 0

    ok = await client.post(
        "/api/transactions", headers=h,
        json={"amount": 5000, "type": "expense", "category_id": groceries,
              "description": "ok", "transaction_date": today},
    )
    assert ok.status_code == 201
    txn_id = ok.json()["id"]
    # Flipping only the type would leave an expense category on an income.
    flip = await client.put(f"/api/transactions/{txn_id}", headers=h, json={"type": "income"})
    assert flip.status_code == 400
    both = await client.put(
        f"/api/transactions/{txn_id}", headers=h,
        json={"type": "income", "category_id": salary},
    )
    assert both.status_code == 200, both.text

    income_budget = await client.post(
        "/api/budgets", headers=h,
        json={"limit_amount": 1000, "period": "monthly", "start_date": today,
              "category_id": salary},
    )
    assert income_budget.status_code == 400


async def test_database_rejects_non_positive_amount(db):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        await db.execute(text(
            "INSERT INTO transactions (id, user_id, amount, type, transaction_date, created_at) "
            "SELECT gen_random_uuid(), id, -1, 'expense', current_date, now() FROM users LIMIT 1"
        ))
    await db.rollback()
