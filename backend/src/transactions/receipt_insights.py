"""Normalize receipt lines for comparison and period analysis."""

from __future__ import annotations

import re
import unicodedata
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.transactions.models import Transaction, TransactionType

ZERO = Decimal(0)
CENT = Decimal(".01")
UNIT_CONVERSIONS = {
    "l": ("l", 1), "л": ("l", 1), "ml": ("l", ".001"), "мл": ("l", ".001"),
    "kg": ("kg", 1), "кг": ("kg", 1), "g": ("kg", ".001"), "г": ("kg", ".001"),
    "pc": ("pc", 1), "pcs": ("pc", 1), "шт": ("pc", 1), "дана": ("pc", 1),
}
PACKAGE_MARK = re.compile(r"\d+(?:[.,]\d+)?\s*(?:кг|kg|мл|ml|л|l|г|g|шт|pc)\b", re.I)
FAT_MARK = re.compile(r"\d+(?:[.,]\d+)?\s*%")
NON_WORD = re.compile(r"[^\w]+", re.UNICODE)


def normalized(value: object) -> str:
    return " ".join(NON_WORD.sub(" ", unicodedata.normalize("NFKC", str(value or "")).casefold()).split())


def number(value: object) -> Decimal:
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else ZERO
    except (ArithmeticError, TypeError):
        return ZERO


def money(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def unit_size(value: object, unit: object) -> tuple[Decimal, str]:
    conversion = UNIT_CONVERSIONS.get(normalized(unit))
    size = number(value)
    if conversion is None or size <= 0:
        return ZERO, ""
    unit_code, ratio = conversion
    return size * Decimal(ratio), unit_code


@dataclass(frozen=True)
class Product:
    name: str
    brand: str = ""
    barcode: str = ""
    variant: str = ""
    fat_percent: str = ""
    package_size: Decimal = ZERO
    unit: str = ""

    @property
    def family(self) -> tuple[str, str, str, str, str]:
        name = normalized(FAT_MARK.sub("", PACKAGE_MARK.sub("", self.name)))
        brand = normalized(self.brand)
        if brand and name.startswith(brand + " "):
            name = name[len(brand) + 1:]
        return brand, name, normalized(self.variant), self.fat_percent, self.unit

    @property
    def key(self) -> str:
        if self.barcode:
            return "gtin:" + self.barcode
        return "|".join((*self.family, format(self.package_size.normalize(), "f")))

    def public(self) -> dict:
        return {
            "name": self.name, "brand": self.brand, "barcode": self.barcode,
            "variant": self.variant, "fat_percent": self.fat_percent,
            "package_size": str(self.package_size) if self.package_size else "",
            "package_unit": self.unit,
        }


def product_from_item(item: dict) -> Product:
    name = str(item.get("name") or "").strip()
    size, unit = unit_size(item.get("package_size"), item.get("package_unit"))
    if not unit:
        match = PACKAGE_MARK.search(name)
        if match:
            stamp = match.group()
            amount = re.match(r"\d+(?:[.,]\d+)?", stamp)
            if amount:
                size, unit = unit_size(amount.group().replace(",", "."), stamp[amount.end():])
    if not unit:
        _, unit = unit_size(1, item.get("unit"))
        # Loose weighted goods have no per-pack size.
        if unit == "pc":
            size = Decimal(1)
    fat = item.get("fat_percent")
    if fat in (None, ""):
        mark = FAT_MARK.search(name)
        fat = mark.group().rstrip("% ").replace(",", ".") if mark else ""
    fat_percent = format(number(fat).normalize(), "f") if fat not in ("", None) else ""
    raw_code = re.sub(r"[^0-9]", "", str(item.get("barcode") or ""))
    barcode = raw_code.zfill(14) if len(raw_code) in (8, 12, 13, 14) else ""
    return Product(name, str(item.get("brand") or ""), barcode, str(item.get("variant") or ""), fat_percent, size, unit)


def match_quality(reference: Product, candidate: Product) -> str | None:
    if reference.barcode and reference.barcode == candidate.barcode:
        return "exact"
    ref_brand, ref_name, ref_variant, ref_fat, ref_unit = reference.family
    cand_brand, cand_name, cand_variant, cand_fat, cand_unit = candidate.family
    if not ref_name or not cand_name:
        return None
    if ref_unit and cand_unit and ref_unit != cand_unit:
        return None
    common = set(ref_name.split()) & set(cand_name.split())
    if ref_name != cand_name and not common:
        return None
    if (ref_brand and cand_brand and ref_brand != cand_brand) or (
        ref_fat and cand_fat and ref_fat != cand_fat
    ) or (ref_variant and cand_variant and ref_variant != cand_variant):
        return "similar"
    reliable = (
        bool(ref_brand) and ref_brand == cand_brand and ref_name == cand_name
        and ref_variant == cand_variant and ref_fat == cand_fat
        and bool(ref_unit) and ref_unit == cand_unit
        and reference.package_size > 0 and candidate.package_size > 0
    )
    if not reliable:
        return "uncertain"
    if reference.package_size != candidate.package_size:
        return "other_package"
    return "uncertain" if reference.barcode and candidate.barcode else "exact"


@dataclass(frozen=True)
class Line:
    tx_id: uuid.UUID
    day: date
    merchant: str
    branch: str
    address: str
    category_id: str | None
    index: int
    product: Product
    quantity: Decimal
    quantity_unit: str
    spend: Decimal
    discount: Decimal
    price: Decimal
    condition: str

    @property
    def store_key(self) -> str:
        return "|".join(normalized(part) for part in (self.merchant, self.branch, self.address))

    @property
    def store_name(self) -> str:
        return " · ".join(part for part in (self.merchant, self.branch, self.address) if part)

    def comparison_quantity(self) -> Decimal:
        if self.product.package_size and self.quantity_unit == "pc":
            return self.product.package_size * self.quantity
        if self.product.unit and self.quantity_unit == self.product.unit:
            return self.quantity
        return ZERO

    def package_price(self) -> Decimal | None:
        if self.quantity_unit == "pc" and self.quantity > 0:
            return self.price
        return None

    def unit_price(self) -> Decimal | None:
        quantity = self.comparison_quantity()
        if not quantity:
            return None
        return self.price * self.quantity / quantity

    def public(self) -> dict:
        return {
            "transaction_id": str(self.tx_id), "day": self.day.isoformat(),
            "merchant": self.merchant, "branch": self.branch, "address": self.address,
            "category_id": self.category_id, "line_index": self.index, "product": self.product.public(),
            "quantity": str(self.quantity), "quantity_unit": self.quantity_unit, "spend": money(self.spend),
            "discount": money(self.discount),
        }


def lines_for(transaction: Transaction) -> list[Line]:
    receipt = (transaction.ai_metadata or {}).get("receipt") or {}
    totals = (receipt.get("totals") or {}).get("line_amounts") or []
    result = []
    for index, item in enumerate(receipt.get("items") or []):
        product = product_from_item(item)
        quantity, unit = unit_size(item.get("quantity"), item.get("unit"))
        if not quantity and number(item.get("quantity")) > 0 and not normalized(item.get("unit")) and product.package_size > 0:
            quantity, unit = number(item["quantity"]), "pc"
        native_quantity = quantity if quantity else number(item.get("quantity"))
        net = number(totals[index]) if index < len(totals) else ZERO
        observed_price = net / native_quantity if native_quantity and net > 0 else ZERO
        result.append(Line(
            transaction.id, transaction.transaction_date, transaction.merchant or "",
            str(receipt.get("branch") or ""), str(receipt.get("branch_address") or ""),
            item.get("category_id"), index, product, quantity, unit, number(item.get("allocated_amount")),
            number(item.get("discount")), observed_price, str(item.get("promotion_condition") or ""),
        ))
    return result


async def receipt_transactions(
    db: AsyncSession, user_id: uuid.UUID, start: date | None = None, end: date | None = None,
) -> list[Transaction]:
    statement = select(Transaction).where(
        Transaction.user_id == user_id, Transaction.type == TransactionType.expense,
        Transaction.ai_metadata["receipt"].is_not(None),
    )
    if start is not None:
        statement = statement.where(Transaction.transaction_date >= start)
    if end is not None:
        statement = statement.where(Transaction.transaction_date <= end)
    return list((await db.scalars(statement.order_by(Transaction.transaction_date.desc(), Transaction.id))).all())


def grouped(lines: list[Line], field: str) -> dict[str, list[Line]]:
    result: dict[str, list[Line]] = defaultdict(list)
    for line in lines:
        key = line.product.key if field == "product" else line.store_key if field == "store" else line.category_id or "-"
        result[key].append(line)
    return result
