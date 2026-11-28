"""Compare purchases and optional retailer-supplied price observations."""

from __future__ import annotations

import os
import re
from datetime import date
from decimal import Decimal
from uuid import UUID

import httpx
from pydantic import BaseModel, Field, HttpUrl, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.deals.locations import cached_json, distance_km
from src.transactions.receipt_insights import (
    Product, lines_for, match_quality, money, normalized, number, product_from_item, receipt_transactions,
)

FEED_URL = os.getenv("SMARTBUDGET_PRICE_FEED_URL", "")


class CatalogOffer(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    brand: str = ""
    barcode: str = ""
    variant: str = ""
    fat_percent: str | None = None
    package_size: str | None = None
    package_unit: str = ""
    store: str = Field(min_length=1)
    branch: str
    address: str = ""
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)
    package_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    date: date
    available: bool | None = None
    condition: str = ""
    source_name: str
    source_url: HttpUrl


async def load_catalog() -> tuple[list[CatalogOffer], bool]:
    if not FEED_URL:
        return [], False
    try:
        data = await cached_json(("prices", FEED_URL), 600, "GET", FEED_URL)
    except (httpx.HTTPError, ValueError):
        return [], False
    rows = []
    if isinstance(data, dict) and isinstance(data.get("offers"), list):
        for item in data["offers"][:2000]:
            try:
                rows.append(CatalogOffer.model_validate(item))
            except ValidationError:
                continue
    return rows, bool(rows)


def score(offers: list[dict], unit: str, cost_per_km: Decimal, allow_conditions: bool) -> dict:
    accepted = [
        row for row in offers
        if row["match"] in ("exact", "other_package") and (allow_conditions or not row["condition"])
        and row["available_today"] is not False
    ]

    def best(key: str, candidates: list[dict], comparable_price: bool = True) -> dict | None:
        candidates = sorted((row for row in candidates if row[key] is not None),
            key=lambda row: (number(row[key]), row["id"]))
        if not candidates:
            return None
        first = candidates[0]
        other = next((row for row in candidates[1:] if row["branch_key"] != first["branch_key"] or row["product"] != first["product"]), None)
        return {
            "offer_id": first["id"], "value": first[key], "compare_id": other["id"] if other else None,
            "savings": money(number(other[key]) - number(first[key])) if other and comparable_price else None,
        }

    for row in offers:
        row["trip_total"] = None
        if cost_per_km > 0 and row["distance_km"] is not None and row["package_price"] is not None:
            row["trip_total"] = money(number(row["package_price"]) + 2 * cost_per_km * number(row["distance_km"]))
    unit_candidates = [row for row in accepted if row["unit"] == unit] if unit else []
    return {
        "cheapest_package": best("package_price", accepted),
        "cheapest_unit": best("unit_price", unit_candidates),
        "closest": best("distance_km", accepted, False),
        "cheapest_with_trip": best("trip_total", accepted),
    }


async def compare(
    db: AsyncSession, user_id: UUID, query: str, reference: Product | None,
    lat: float | None, lon: float | None, radius: float, cost_per_km: Decimal, allow_conditions: bool,
    branches: list[dict],
) -> dict:
    transactions = await receipt_transactions(db, user_id)
    catalog, has_catalog = await load_catalog()
    current_day = date.today()
    search = set(normalized(query).split())
    search_barcode = re.sub(r"[^0-9]", "", query) if re.fullmatch(r"[0-9\s-]+", query) else ""
    if search_barcode:
        search_barcode = search_barcode.zfill(14)
    offers: list[dict] = []
    unique = set()

    def classification(product: Product) -> str | None:
        if reference is not None:
            return match_quality(reference, product)
        haystack = set(normalized(f"{product.name} {product.brand} {product.variant}").split())
        if search_barcode:
            return "exact" if product.barcode == search_barcode else None
        return "search" if search and all(any(term in word for word in haystack) for term in search) else None

    def append(
        product: Product, store: str, branch: str, address: str, day: date,
        pack: Decimal | None, price: Decimal | None, condition: str, source_name: str,
        source_kind: str, source_url: str | None = None, available: bool | None = None,
        coordinates: tuple[float, float] | None = None,
    ) -> None:
        kind = classification(product)
        if kind is None or (pack is None and price is None) or day > current_day:
            return
        branch_key = "|".join(map(normalized, (store, branch, address)))
        key = (source_kind, branch_key, product.key, normalized(condition))
        if key in unique:
            return
        if coordinates is None and address:
            store_tokens = set(normalized(store).split())
            for entry in branches:
                found_address = normalized(entry.get("address"))
                if found_address and found_address == normalized(address) and store_tokens & set(normalized(entry["name"]).split()):
                    coordinates = entry["lat"], entry["lon"]
                    break
        distance = None
        if coordinates and lat is not None and lon is not None:
            distance = round(distance_km(lat, lon, *coordinates), 2)
            if distance > radius:
                return
        unique.add(key)
        offers.append({
            "id": str(len(offers) + 1), "product": product.public(), "unit": product.unit, "match": kind,
            "store": store, "branch": branch, "address": address, "branch_key": branch_key,
            "package_price": money(pack) if pack is not None else None,
            "unit_price": money(price) if price is not None else None,
            "distance_km": distance, "date": day.isoformat(), "source_kind": source_kind,
            "source_name": source_name, "source_url": source_url, "condition": condition,
            "available_today": available if day == current_day and source_kind == "catalog" else None,
            "current_price_verified": day == current_day and source_kind == "catalog",
            "age_days": (current_day - day).days,
            "lat": coordinates[0] if coordinates else None, "lon": coordinates[1] if coordinates else None,
        })

    for record in sorted(catalog, key=lambda offer: offer.date, reverse=True):
        product = product_from_item(record.model_dump())
        append(product, record.store, record.branch, record.address, record.date, record.package_price,
            record.package_price / product.package_size if product.package_size else None, record.condition,
            record.source_name, "catalog", str(record.source_url), record.available,
            (record.lat, record.lon) if record.lat is not None and record.lon is not None else None)
    for tx in transactions:
        for line in lines_for(tx):
            append(line.product, line.merchant, line.branch, line.address, line.day,
                line.package_price(), line.unit_price(), line.condition, "receipt", "receipt")
    units = {row["unit"] for row in offers if row["match"] == "exact" and row["unit"]}
    unit = reference.unit if reference else units.pop() if len(units) == 1 else ""
    return {
        "offers": offers, "recommendations": score(offers, unit, cost_per_km, allow_conditions),
        "catalog_available": has_catalog,
    }
