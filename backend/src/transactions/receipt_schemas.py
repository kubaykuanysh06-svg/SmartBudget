"""Receipt extraction, review, and accounting data."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from src.transactions.schemas import MAX_AMOUNT, TransactionResponse

Money = Annotated[Decimal, Field(ge=0, le=MAX_AMOUNT, decimal_places=2, allow_inf_nan=False)]
Quantity = Annotated[Decimal, Field(gt=0, le=1000000, decimal_places=6, allow_inf_nan=False)]


class ExtractedItem(BaseModel):
    name: str | None
    brand: str | None = None
    barcode: str | None = None
    variant: str | None = None
    fat_percent: float | None = None
    package_size: float | None = None
    package_unit: str | None = None
    promotion_condition: str | None = None
    quantity: float | None
    unit: str | None
    unit_price: float | None
    discount: float | None
    line_total: float | None
    line_total_is_net: bool | None
    suggested_category: str | None
    uncertain_fields: list[str]


class ExtractedReceipt(BaseModel):
    is_receipt: bool
    merchant: str | None
    branch: str | None = None
    branch_address: str | None = None
    purchase_date: str | None
    receipt_number: str | None
    currency: str | None
    paid: float | None
    order_discount: float | None
    fees: float | None
    items: list[ExtractedItem]
    uncertain_fields: list[str]


class ReceiptItem(BaseModel):
    name: str = Field(default="", max_length=255)
    brand: str = Field(default="", max_length=120)
    barcode: str = Field(default="", pattern=r"^(?:[0-9]{8}|[0-9]{12,14})?$")
    variant: str = Field(default="", max_length=120)
    fat_percent: Annotated[Decimal, Field(ge=0, le=100, decimal_places=3, allow_inf_nan=False)] | None = None
    package_size: Quantity | None = None
    package_unit: str = Field(default="", max_length=24)
    promotion_condition: str = Field(default="", max_length=250)
    quantity: Quantity | None = None
    unit: str = Field(default="", max_length=24)
    unit_price: Money | None = None
    discount: Money | None = None
    line_total: Money | None = None
    line_total_is_net: bool | None = None
    category_id: UUID | None = None


class ReceiptDraft(BaseModel):
    merchant: str = Field(default="", max_length=255)
    branch: str = Field(default="", max_length=160)
    branch_address: str = Field(default="", max_length=255)
    purchase_date: date | None = None
    receipt_number: str = Field(default="", max_length=120)
    currency: Literal["KZT"] = "KZT"
    paid: Money | None = None
    order_discount: Money = Decimal(0)
    fees: Money = Decimal(0)
    confirm_paid: bool = False
    items: list[ReceiptItem] = Field(default_factory=list, max_length=250)


class ReceiptCreate(ReceiptDraft):
    upload_token: str = Field(max_length=1500)


class ReceiptTotals(BaseModel):
    subtotal: Decimal
    item_discounts: Decimal
    order_discount: Decimal
    fees: Decimal
    calculated: Decimal
    paid: Decimal | None
    difference: Decimal | None
    line_amounts: list[Decimal]


class ReceiptResult(BaseModel):
    transaction: TransactionResponse
    duplicate: bool = False


class ReceiptUpload(BaseModel):
    upload_token: str | None = None
    extraction: ExtractedReceipt | None = None
    duplicate: TransactionResponse | None = None
