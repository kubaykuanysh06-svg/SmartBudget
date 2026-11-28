"""Receipt period analysis and drill-downs."""

from datetime import date, timedelta
from decimal import Decimal
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.analytics.services import receipt_report
from src.categories.services import list_categories
from src.core.exceptions import BadRequest
from src.transactions.receipt_insights import Line, ZERO, grouped, lines_for, money, number, receipt_transactions

Group = Literal["category", "store", "product"]


def change_value(current: Decimal, previous: Decimal) -> dict:
    delta = current - previous
    return {
        "current": money(current), "previous": money(previous), "difference": money(delta),
        "percent": money(100 * delta / previous) if previous else None,
    }


def movement(current: list[Line], previous: list[Line]) -> dict | None:
    if not current or not previous or any(not line.comparison_quantity() for line in current + previous):
        return None
    units = {line.product.unit for line in current + previous}
    if len(units) != 1:
        return None
    current_qty = sum((line.comparison_quantity() for line in current), ZERO)
    previous_qty = sum((line.comparison_quantity() for line in previous), ZERO)
    if not current_qty or not previous_qty:
        return None
    current_cost = sum(line.spend for line in current)
    previous_cost = sum(line.spend for line in previous)
    current_price, previous_price = current_cost / current_qty, previous_cost / previous_qty
    price_effect = Decimal(money((current_price - previous_price) * previous_qty))
    return {
        "unit": units.pop(), "current_quantity": str(current_qty), "previous_quantity": str(previous_qty),
        "current_unit_cost": money(current_price), "previous_unit_cost": money(previous_price),
        "price_effect": money(price_effect), "quantity_effect": money(current_cost - previous_cost - price_effect),
    }


def _date_window(start: date, end: date) -> tuple[date, date]:
    days = (end - start).days + 1
    if days < 1 or days > 366 or start.year < 2:
        raise BadRequest("Choose a date range of 1 to 366 days")
    return start - timedelta(days=days), start - timedelta(days=1)


async def deep_report(db: AsyncSession, user_id: UUID, start: date, end: date) -> dict:
    first, last = _date_window(start, end)
    transactions = await receipt_transactions(db, user_id, first, end)
    current_tx = [tx for tx in transactions if tx.transaction_date >= start]
    previous_tx = [tx for tx in transactions if tx.transaction_date < start]
    current_lines = [line for tx in current_tx for line in lines_for(tx)]
    previous_lines = [line for tx in previous_tx for line in lines_for(tx)]
    category_names = {str(category.id): category.name for category in await list_categories(db, user_id)}
    current_total = sum((tx.amount for tx in current_tx), ZERO)
    previous_total = sum((tx.amount for tx in previous_tx), ZERO)

    def report_group(field: Group) -> list[dict]:
        current, previous = grouped(current_lines, field), grouped(previous_lines, field)
        response = []
        for key in current.keys() | previous.keys():
            now, before = current.get(key, []), previous.get(key, [])
            sample = (now or before)[0]
            label = sample.product.name if field == "product" else (
                sample.store_name if field == "store" else category_names.get(key)
            )
            row = change_value(sum((line.spend for line in now), ZERO), sum((line.spend for line in before), ZERO))
            response.append({
                "key": key, "name": label, **row,
                "share": money(Decimal(row["current"]) / current_total * 100) if current_total else "0.00",
                "purchase_count": len({line.tx_id for line in now}),
                "movement": movement(now, before) if field == "product" else None,
            })
        return sorted(response, key=lambda row: (-Decimal(row["current"]), row["key"]))

    products = report_group("product")
    categories = report_group("category")
    stores = report_group("store")
    # Budget remainders follow every expense, as on the budgets page.
    prior_report = await receipt_report(db, user_id, start, end, budget_receipts_only=False)
    selected = sorted(products, key=lambda row: (-row["purchase_count"], row["key"]))[:15]
    all_product_lines = grouped(current_lines + previous_lines, "product")
    history = []
    for row in selected:
        if row["purchase_count"] < 2:
            continue
        observations = []
        for line in all_product_lines[row["key"]]:
            unit_price, package_price = line.unit_price(), line.package_price()
            if unit_price is None and package_price is None:
                continue
            observations.append({
                "day": line.day.isoformat(), "store": line.store_name,
                "unit_price": money(unit_price) if unit_price is not None else None,
                "package_price": money(package_price) if package_price is not None else None,
                "unit": line.product.unit, "transaction_id": str(line.tx_id),
            })
        if observations:
            history.append({"key": row["key"], "name": row["name"], "observations": observations[:80]})
    discounts = ZERO
    for tx in current_tx:
        totals = ((tx.ai_metadata or {}).get("receipt") or {}).get("totals") or {}
        discounts += number(totals.get("item_discounts")) + number(totals.get("order_discount"))

    def top_growth(rows: list[dict]) -> dict | None:
        top = max(rows, key=lambda row: Decimal(row["difference"]), default=None)
        return top if top and Decimal(top["difference"]) > 0 else None

    return {
        "totals": change_value(current_total, previous_total),
        "previous_from": first, "previous_to": last, "has_previous": bool(previous_tx),
        "purchase_count": len(current_tx),
        "average_receipt": money(current_total / len(current_tx)) if current_tx else "0.00",
        "discount_total": money(discounts), "stores": stores, "categories": categories, "products": products,
        "top_category_growth": top_growth(categories), "top_product_growth": top_growth(products),
        "budgets": prior_report.budgets, "history": history,
    }


async def drilldown(db: AsyncSession, user_id: UUID, start: date, end: date, group: Group, key: str, offset: int) -> dict:
    _date_window(start, end)
    transactions = await receipt_transactions(db, user_id, start, end)
    rows = grouped([line for tx in transactions for line in lines_for(tx)], group).get(key, [])
    return {"total": len(rows), "rows": [line.public() for line in rows[offset:offset + 50]]}
