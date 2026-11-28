"""Receipt analytics and price comparison scenarios."""

from __future__ import annotations

import random
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from jose import jwt

from src.core.config import settings
from tests.conftest import register_and_login

TODAY = date.today()


def upload_token(user_id: str, tag: str) -> str:
    return jwt.encode(
        {
            "sub": user_id, "type": "receipt-upload", "file_hash": f"hash-{tag}",
            "identity_hash": None, "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        settings.SECRET_KEY, algorithm=settings.ALGORITHM,
    )


def new_brand() -> str:
    """Prices are shared by all users, so each test uses its own brand to stay independent."""
    return "Br" + uuid.uuid4().hex[:8]


def new_barcode() -> str:
    return "487" + "".join(random.choice("0123456789") for _ in range(10))


def reference_for(brand: str, size: str = "1") -> dict:
    return {"name": f"Молоко {brand} 2,5% {size} л", "brand": brand, "variant": "пастерленген",
            "fat_percent": "2.5", "package_size": size, "package_unit": "л"}


def milk(size: str, price: str, quantity: str = "1", brand: str = "Lactel", **extra) -> dict:
    return {
        "name": f"Молоко {brand} 2,5% {size} л", "brand": brand, "variant": "пастерленген",
        "fat_percent": "2.5", "package_size": size, "package_unit": "л", "quantity": quantity,
        "unit": "шт", "unit_price": price, "line_total": str(Decimal(price) * Decimal(quantity)),
        "discount": "0", **extra,
    }


async def save_receipt(client, auth, tag: str, merchant: str, day: date, items: list[dict], **header) -> dict:
    gross = sum(Decimal(item["line_total"]) - Decimal(item.get("discount") or 0) for item in items)
    body = {
        "merchant": merchant, "purchase_date": day.isoformat(), "receipt_number": tag,
        "paid": str(gross), "items": items, "upload_token": upload_token(auth["user"]["id"], tag), **header,
    }
    res = await client.post("/api/receipts", json=body, headers=auth["headers"])
    assert res.status_code == 201, res.text
    return res.json()["transaction"]


async def test_unit_price_and_package_price_are_reported_separately(client):
    auth = await register_and_login(client, "Milk")
    brand = new_brand()
    await save_receipt(client, auth, "a", "Magnum", TODAY, [milk("0.9", "540", brand=brand)], branch="Абай 10")
    await save_receipt(client, auth, "b", "Small", TODAY, [milk("1", "580", brand=brand)], branch="Сейфуллин 5")

    reference = reference_for(brand)
    res = await client.post("/api/shopping/compare", json={"reference": reference}, headers=auth["headers"])
    assert res.status_code == 200, res.text
    data = res.json()
    by_id = {row["id"]: row for row in data["offers"]}
    ours = [row for row in data["offers"] if row["product"]["brand"] == brand]
    assert {row["match"] for row in ours} == {"exact", "other_package"}
    assert all(row["match"] not in ("exact", "other_package") for row in data["offers"] if row not in ours)

    package = data["recommendations"]["cheapest_package"]
    assert by_id[package["offer_id"]]["store"] == "Magnum"
    assert Decimal(package["value"]) == Decimal("540")
    assert Decimal(package["savings"]) == Decimal("40")

    unit = data["recommendations"]["cheapest_unit"]
    assert by_id[unit["offer_id"]]["store"] == "Small"
    assert Decimal(unit["value"]) == Decimal("580")
    assert Decimal(unit["savings"]) == Decimal("20")
    assert Decimal(by_id[unit["compare_id"]]["unit_price"]) == Decimal("600")

    # Receipt prices are recorded observations, not verified current prices.
    assert all(row["source_kind"] == "receipt" and not row["current_price_verified"] for row in ours)
    assert all(row["own_receipt"] and row["date"] == TODAY.isoformat() for row in ours)


async def test_branches_conditions_and_old_prices(client):
    auth = await register_and_login(client, "Branches")
    brand = new_brand()
    old_day = TODAY - timedelta(days=40)
    await save_receipt(client, auth, "c1", "Magnum", old_day, [milk("1", "560", brand=brand)], branch="№12", branch_address="Абай 10")
    await save_receipt(client, auth, "c2", "Magnum", TODAY, [milk("1", "600", brand=brand)], branch="№7", branch_address="Төле би 4")
    await save_receipt(
        client, auth, "c3", "Small", TODAY,
        [milk("1", "590", brand=brand, discount="50", line_total_is_net=False, promotion_condition="Small Club картасымен")],
    )
    reference = reference_for(brand)

    res = await client.post("/api/shopping/compare", json={"reference": reference}, headers=auth["headers"])
    data = res.json()
    magnum = [row for row in data["offers"] if row["store"] == "Magnum" and row["product"]["brand"] == brand]
    assert {row["branch"] for row in magnum} == {"№12", "№7"}, "each branch is a separate offer"
    old = next(row for row in magnum if row["branch"] == "№12")
    assert old["age_days"] == 40 and old["date"] == old_day.isoformat()
    conditional = next(row for row in data["offers"] if row["store"] == "Small" and row["product"]["brand"] == brand)
    assert conditional["condition"] == "Small Club картасымен"
    assert Decimal(conditional["package_price"]) == Decimal("540")
    by_id = {row["id"]: row for row in data["offers"]}
    best = by_id[data["recommendations"]["cheapest_package"]["offer_id"]]
    assert best["store"] == "Magnum" and best["branch"] == "№12", "conditional offers are excluded by default"

    res = await client.post("/api/shopping/compare", json={"reference": reference, "allow_conditions": True},
                            headers=auth["headers"])
    data = res.json()
    by_id = {row["id"]: row for row in data["offers"]}
    assert by_id[data["recommendations"]["cheapest_package"]["offer_id"]]["store"] == "Small"


async def test_similar_and_uncertain_matches_are_marked(client):
    auth = await register_and_login(client, "Similar")
    brand = new_brand()
    await save_receipt(client, auth, "s1", "Magnum", TODAY, [
        milk("1", "580", brand=brand),
        {**milk("1", "520", brand=brand), "name": f"Молоко {brand} 3,2% 1 л", "fat_percent": "3.2"},
        {"name": "Молоко 1 л", "quantity": "1", "unit": "шт", "unit_price": "450", "line_total": "450"},
    ])
    reference = reference_for(brand)
    res = await client.post("/api/shopping/compare", json={"reference": reference}, headers=auth["headers"])
    matches = {row["product"]["name"]: row["match"] for row in res.json()["offers"]}
    assert matches[f"Молоко {brand} 2,5% 1 л"] == "exact"
    assert matches[f"Молоко {brand} 3,2% 1 л"] == "similar"
    assert matches["Молоко 1 л"] == "uncertain"


async def test_barcode_identifies_the_same_product(client):
    auth = await register_and_login(client, "Barcode")
    code = new_barcode()
    await save_receipt(client, auth, "b1", "Magnum", TODAY, [milk("1", "580", barcode=code)])
    await save_receipt(client, auth, "b2", "Anvar", TODAY, [
        {**milk("1", "570", barcode=code), "name": "LACTEL сүт", "brand": ""},
    ])
    res = await client.post("/api/shopping/compare", json={"query": code}, headers=auth["headers"])
    data = res.json()
    assert {row["store"] for row in data["offers"]} == {"Magnum", "Anvar"}
    assert all(row["match"] == "exact" for row in data["offers"])


async def test_trip_cost_changes_the_best_offer(client):
    from src.deals.comparison import score

    def offer(identifier: str, price: str, distance: float) -> dict:
        return {"id": identifier, "match": "exact", "condition": "", "available_today": None, "unit": "l",
                "package_price": price, "unit_price": price, "distance_km": distance,
                "branch_key": identifier, "product": {}}

    rows = [offer("far", "500", 6.0), offer("near", "560", 0.5)]
    result = score(rows, "l", Decimal("10"), False)
    assert result["cheapest_package"]["offer_id"] == "far"
    assert result["closest"]["offer_id"] == "near"
    # far: 500 + 2*6*10 = 620; near: 560 + 2*0.5*10 = 570
    assert result["cheapest_with_trip"]["offer_id"] == "near"
    assert Decimal(result["cheapest_with_trip"]["savings"]) == Decimal("50")


async def test_period_analytics_and_drilldown(client):
    auth = await register_and_login(client, "Analytics")
    start = TODAY.replace(day=1)
    end = TODAY
    previous_day = start - timedelta(days=3)
    await save_receipt(client, auth, "p1", "Magnum", previous_day, [milk("1", "500", "2")])
    await save_receipt(client, auth, "p2", "Magnum", start, [milk("1", "600", "3")])
    await save_receipt(client, auth, "p3", "Small", start, [
        {"name": "Нан", "quantity": "1", "unit": "шт", "unit_price": "200", "line_total": "200",
         "discount": "20", "line_total_is_net": False},
    ])
    params = {"date_from": start.isoformat(), "date_to": end.isoformat()}
    res = await client.get("/api/analytics/receipt-details", params=params, headers=auth["headers"])
    assert res.status_code == 200, res.text
    report = res.json()
    assert Decimal(report["totals"]["current"]) == Decimal("1980")
    assert report["purchase_count"] == 2
    assert Decimal(report["average_receipt"]) == Decimal("990")
    assert Decimal(report["discount_total"]) == Decimal("20")
    assert {row["name"] for row in report["stores"]} == {"Magnum", "Small"}

    bread = next(row for row in report["products"] if row["name"] == "Нан")
    assert bread["percent"] is None and Decimal(bread["difference"]) == Decimal("180"), "zero base shows tenge change"

    milk_row = next(row for row in report["products"] if row["name"].startswith("Молоко"))
    move = milk_row["movement"]
    # 1000 -> 1800: price effect (600-500)*2 = 200, quantity effect 600.
    assert Decimal(move["price_effect"]) == Decimal("200")
    assert Decimal(move["quantity_effect"]) == Decimal("600")
    assert report["top_product_growth"]["name"].startswith("Молоко")

    res = await client.get("/api/analytics/receipt-lines", headers=auth["headers"],
                           params={**params, "group": "product", "key": milk_row["key"]})
    lines = res.json()
    assert lines["total"] == 1 and lines["rows"][0]["merchant"] == "Magnum"


async def test_analytics_follow_receipt_edits_and_deletes(client):
    auth = await register_and_login(client, "Edits")
    tx = await save_receipt(client, auth, "e1", "Magnum", TODAY, [milk("1", "600")])
    params = {"date_from": TODAY.isoformat(), "date_to": TODAY.isoformat()}

    draft = {**tx["ai_metadata"]["receipt"], "paid": "700", "items": [milk("1", "700")]}
    res = await client.put(f"/api/receipts/{tx['id']}", json=draft, headers=auth["headers"])
    assert res.status_code == 200, res.text
    report = (await client.get("/api/analytics/receipt-details", params=params, headers=auth["headers"])).json()
    assert Decimal(report["totals"]["current"]) == Decimal("700")

    res = await client.delete(f"/api/transactions/{tx['id']}", headers=auth["headers"])
    assert res.status_code == 204, res.text
    report = (await client.get("/api/analytics/receipt-details", params=params, headers=auth["headers"])).json()
    assert Decimal(report["totals"]["current"]) == 0 and report["products"] == []
