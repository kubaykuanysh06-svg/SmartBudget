"""AI Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class CategorizeSuggestion(BaseModel):
    category_name: str
    confidence: float
    reasoning: str


class PriceAnalysis(BaseModel):
    verdict: str  # good_deal / fair / overpriced
    estimated_fair_price: float | None = None
    savings_or_overpay: float | None = None
    explanation: str


class InsightResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    content: str
    metadata: dict | None = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


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
