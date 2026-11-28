"""Shared price catalogue, store branches and location scenarios."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import httpx
import pytest
from sqlalchemy import func, select

from src.deals import comparison, locations
from src.deals.catalog_models import PriceObservation, ReceiptItem, StoreBranch
from tests.conftest import register_and_login
from tests.test_receipt_insights import milk, new_brand, reference_for, save_receipt

TODAY = date.today()
CENTER = (44.8488, 65.4823)  # Kyzylorda


def osm_store(identifier: int, name: str, lat: float, lon: float, street: str, number: str) -> dict:
    return {"type": "node", "id": identifier, "lat": lat, "lon": lon,
            "tags": {"name": name, "shop": "supermarket", "addr:street": street, "addr:housenumber": number}}


@pytest.fixture
def fake_map(monkeypatch):
    """Overpass answer with two branches of one chain, another chain, and one store outside the radius."""
    elements = [
        osm_store(1, "Magnum", 44.8530, 65.4823, "Абай", "10"),       # ~0.47 km
        osm_store(2, "Magnum", 44.8700, 65.4823, "Төле би", "4"),     # ~2.36 km
        osm_store(3, "Small", 44.8488, 65.4900, "Сейфуллин", "5"),    # ~0.61 km
        osm_store(4, "Magnum", 44.9500, 65.4823, "Шалғай", "1"),      # ~11 km, outside 3 km
    ]
    calls = []

    async def fake_json(key, ttl, method, url, **options):
        calls.append(url)
        if key[0] == "stores":
            return {"elements": elements}
        raise httpx.ConnectError("offline in tests")

    locations.CACHE.clear()
    monkeypatch.setattr(locations, "cached_json", fake_json)
    return calls


async def test_receipt_prices_remain_private(client):
    brand = new_brand()
    alice = await register_and_login(client, "Alice")
    bob = await register_and_login(client, "Bob")
    tx = await save_receipt(client, alice, "shared-a", "Magnum", TODAY, [milk("1", "580", brand=brand)])
    await save_receipt(client, bob, "shared-b", "Small", TODAY, [milk("1", "560", brand=brand)])

    res = await client.post("/api/shopping/compare", json={"reference": reference_for(brand)}, headers=bob["headers"])
    assert res.status_code == 200, res.text
    rows = {row["store"]: row for row in res.json()["offers"] if row["product"]["brand"] == brand}
    assert set(rows) == {"Small"}
    assert rows["Small"]["own_receipt"] is True and rows["Small"]["transaction_id"]

    res = await client.post("/api/shopping/compare", json={"reference": reference_for(brand)}, headers=alice["headers"])
    mine = next(row for row in res.json()["offers"] if row["store"] == "Magnum" and row["product"]["brand"] == brand)
    assert mine["transaction_id"] == tx["id"]


async def test_receipt_rows_keep_printed_name_and_follow_edits_and_deletes(client, db):
    brand = new_brand()
    auth = await register_and_login(client, "Rows")
    printed = f"МОЛОКО {brand} 2,5% 1Л ПАСТ"
    tx = await save_receipt(client, auth, "rows", "Magnum", TODAY, [
        {**milk("1", "600", brand=brand), "name": printed},
        {"name": "Нан бородинский", "quantity": "1", "unit": "шт", "unit_price": "250", "line_total": "250"},
    ], branch="№3", branch_address="Абай 10")

    items = (await db.scalars(select(ReceiptItem).where(ReceiptItem.transaction_id == tx["id"])
                              .order_by(ReceiptItem.line_index))).all()
    assert [item.original_name for item in items] == [printed, "Нан бородинский"]
    assert items[0].package_price == Decimal(600) and items[0].unit_price == Decimal(600)
    branch = await db.get(StoreBranch, items[0].branch_id)
    assert (branch.name, branch.address) == ("№3", "Абай 10")

    draft = {**tx["ai_metadata"]["receipt"], "paid": "650", "items": [milk("1", "650", brand=brand)]}
    res = await client.put(f"/api/receipts/{tx['id']}", json=draft, headers=auth["headers"])
    assert res.status_code == 200, res.text
    db.expire_all()
    prices = (await db.scalars(
        select(PriceObservation.package_price).join(ReceiptItem).where(ReceiptItem.transaction_id == tx["id"])
    )).all()
    assert prices == [Decimal(650)]

    res = await client.delete(f"/api/transactions/{tx['id']}", headers=auth["headers"])
    assert res.status_code == 204
    left = await db.scalar(select(func.count()).select_from(ReceiptItem).where(ReceiptItem.transaction_id == tx["id"]))
    assert left == 0
    res = await client.post("/api/shopping/compare", json={"reference": reference_for(brand)}, headers=auth["headers"])
    assert [row for row in res.json()["offers"] if row["product"]["brand"] == brand] == []


async def test_branches_in_radius_are_listed_by_distance(client, fake_map):
    auth = await register_and_login(client, "Map")
    res = await client.post("/api/shopping/branches", json={"lat": CENTER[0], "lon": CENTER[1], "radius": 3},
                            headers=auth["headers"])
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["available"] is True
    names = [(row["name"], row["address"]) for row in data["branches"]]
    assert names == [("Magnum", "Абай 10"), ("Small", "Сейфуллин 5"), ("Magnum", "Төле би 4")]
    distances = [row["distance_km"] for row in data["branches"]]
    assert distances == sorted(distances) and distances[-1] < 3


async def test_comparison_uses_branch_distance_and_trip_cost(client, db, fake_map):
    brand = new_brand()
    auth = await register_and_login(client, "Trip")
    await save_receipt(client, auth, "t1", "Magnum", TODAY, [milk("1", "560", brand=brand)],
                       branch="№1", branch_address="Абай 10")
    await save_receipt(client, auth, "t2", "Magnum", TODAY, [milk("1", "530", brand=brand)],
                       branch="№2", branch_address="Төле би 4")
    body = {"reference": reference_for(brand), "area": {"lat": CENTER[0], "lon": CENTER[1], "radius": 3},
            "cost_per_km": "20"}
    res = await client.post("/api/shopping/compare", json=body, headers=auth["headers"])
    assert res.status_code == 200, res.text
    data = res.json()
    rows = {row["branch"]: row for row in data["offers"] if row["product"]["brand"] == brand}
    assert set(rows) == {"№1", "№2"}, "two branches of one chain keep separate prices"
    assert 0.4 < rows["№1"]["distance_km"] < 0.6 and 2.2 < rows["№2"]["distance_km"] < 2.5
    by_id = {row["id"]: row for row in data["offers"]}
    rec = data["recommendations"]
    assert by_id[rec["cheapest_package"]["offer_id"]]["branch"] == "№2"
    assert by_id[rec["closest"]["offer_id"]]["branch"] == "№1"
    # №1: 560 + 2*0.47*20 ≈ 579; №2: 530 + 2*2.36*20 ≈ 624 → the closer branch wins with travel.
    best = by_id[rec["cheapest_with_trip"]["offer_id"]]
    assert best["branch"] == "№1"
    assert by_id[rec["cheapest_with_trip"]["compare_id"]]["branch"] == "№2"
    assert Decimal(rec["cheapest_with_trip"]["savings"]) > 0

    # The matched map position is stored on the branch for the next comparison.
    db.expire_all()
    branch = (await db.scalars(select(StoreBranch).where(StoreBranch.name == "№1", StoreBranch.address == "Абай 10"))).first()
    assert branch.osm_ref == "node/1" and branch.lat == pytest.approx(44.8530)


async def test_manual_city_works_without_geolocation_or_network(client, fake_map):
    auth = await register_and_login(client, "Manual")
    for lang, name in (("kk", "Қызылорда"), ("ru", "Кызылорда"), ("en", "Kyzylorda")):
        res = await client.get("/api/shopping/places", params={"query": name, "lang": lang}, headers=auth["headers"])
        assert res.status_code == 200, res.text
        assert res.json()[0] == {"name": name, "lat": CENTER[0], "lon": CENTER[1]}
    assert fake_map == [], "a known city needs no geocoder call"
    # A free-text address falls back gracefully when the geocoder is unreachable.
    res = await client.get("/api/shopping/places", params={"query": "Абай даңғылы 10", "lang": "kk"},
                           headers=auth["headers"])
    assert res.status_code == 200 and res.json() == []


async def test_route_is_null_without_a_route_service(client):
    auth = await register_and_login(client, "Route")
    res = await client.post("/api/shopping/route", headers=auth["headers"],
                            json={"lat": CENTER[0], "lon": CENTER[1], "to_lat": 44.85, "to_lon": 65.49})
    assert res.status_code == 200 and res.json() is None


async def test_verified_price_today_is_kept_apart_from_receipt_prices(client, monkeypatch):
    brand = new_brand()
    auth = await register_and_login(client, "Feed")
    await save_receipt(client, auth, "f1", "Magnum", TODAY - timedelta(days=9), [milk("1", "590", brand=brand)])
    offer = comparison.CatalogOffer(
        name=f"Молоко {brand} 2,5% 1 л", brand=brand, variant="пастерленген", fat_percent="2.5",
        package_size="1", package_unit="л", store="Small", branch="№4", package_price=Decimal(575),
        date=TODAY, available=True, condition="2 дана алғанда", source_name="Small прайс",
        source_url="https://example.com/prices",
    )

    async def fake_catalog():
        return [offer], True

    monkeypatch.setattr(comparison, "load_catalog", fake_catalog)
    res = await client.post("/api/shopping/compare", json={"reference": reference_for(brand)}, headers=auth["headers"])
    data = res.json()
    rows = {row["source_kind"]: row for row in data["offers"] if row["product"]["brand"] == brand}
    assert data["catalog_available"] is True
    assert rows["catalog"]["current_price_verified"] and rows["catalog"]["available_today"] is True
    assert rows["catalog"]["condition"] == "2 дана алғанда"
    assert not rows["receipt"]["current_price_verified"] and rows["receipt"]["available_today"] is None
    assert rows["receipt"]["age_days"] == 9


async def test_zero_previous_period_reports_change_in_tenge(client):
    auth = await register_and_login(client, "Zero")
    await save_receipt(client, auth, "z1", "Magnum", TODAY, [milk("1", "480", brand=new_brand())])
    params = {"date_from": TODAY.isoformat(), "date_to": TODAY.isoformat()}
    report = (await client.get("/api/analytics/receipt-details", params=params, headers=auth["headers"])).json()
    assert report["has_previous"] is False
    assert report["totals"]["percent"] is None
    assert Decimal(report["totals"]["difference"]) == Decimal(480)
    assert Decimal(report["stores"][0]["share"]) == Decimal(100)
