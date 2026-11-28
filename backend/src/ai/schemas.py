"""AI Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CategorizeSuggestion(BaseModel):
    category_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class PriceAnalysis(BaseModel):
    verdict: Literal["good_deal", "fair", "overpriced"]
    estimated_fair_price: float | None = None
    savings_or_overpay: float | None = None
    explanation: str


class InsightResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    content: str
    metadata: dict | None = Field(default=None, validation_alias="insight_metadata")
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class ReceiptDetails(BaseModel):
    total: float | None
    currency: str | None
    merchant: str | None
    purchase_date: str | None


class ImageAnalysis(ChatResponse):
    receipt: ReceiptDetails | None


class ImageAnalysisResponse(ImageAnalysis):
    receipt_request_id: uuid.UUID | None = None


class SavingsTip(BaseModel):
    title: str
    description: str
    estimated_monthly_savings: float | None = None
    category: str | None = None


class CategorizationRequest(BaseModel):
    description: str
    merchant: str | None = None
    amount: float


class PriceAnalysisRequest(BaseModel):
    description: str
    merchant: str | None = None
    amount: float
