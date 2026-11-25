"""AI service — Gemini API integration."""

from __future__ import annotations

import json
import uuid

from fastapi import HTTPException
from google import genai
from google.genai import errors
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.models import AiInsight
from src.ai.prompts import (
    CATEGORIZE_PROMPT,
    CHAT_SYSTEM_PROMPT,
    PRICE_ANALYSIS_PROMPT,
    SAVINGS_TIPS_PROMPT,
)
from src.ai.schemas import (
    CategorizeSuggestion,
    ChatResponse,
    InsightResponse,
    PriceAnalysis,
    SavingsTip,
)
from src.core.config import settings

# ── Gemini client helper ──────────────────────────────────


_PLACEHOLDER_GEMINI_KEYS = {"", "your-gemini-api-key", "change-me"}


async def _call_gemini(prompt: str) -> str:
    """Call the Gemini API and return the text response."""
    api_key = settings.GEMINI_API_KEY.strip()
    if api_key in _PLACEHOLDER_GEMINI_KEYS:
        raise HTTPException(status_code=503, detail="Gemini API key is not configured")

    try:
        async with genai.Client(api_key=settings.GEMINI_API_KEY).aio as client:
            response = await client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
            )
    except errors.APIError:
        raise HTTPException(status_code=502, detail="Gemini could not answer the request") from None
    if not response.text:
        raise HTTPException(status_code=502, detail="Gemini returned an empty response")
    return response.text


def _parse_json(text: str) -> dict | list:
    """Extract JSON from a Gemini response that may have markdown fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = lines[1:]  # remove opening ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    return json.loads(cleaned)


# ── Public API ────────────────────────────────────────────


async def auto_categorize(
    description: str,
    merchant: str | None,
    amount: float,
    categories: list[str],
) -> CategorizeSuggestion:
    prompt = CATEGORIZE_PROMPT.format(
        categories=", ".join(categories),
        description=description,
        merchant=merchant or "N/A",
        amount=amount,
    )
    raw = await _call_gemini(prompt)
    data = _parse_json(raw)
    return CategorizeSuggestion(**data)


async def analyze_price(
    description: str,
    merchant: str | None,
    amount: float,
    currency: str,
    price_history: str = "No history available",
) -> PriceAnalysis:
    prompt = PRICE_ANALYSIS_PROMPT.format(
        description=description,
        merchant=merchant or "N/A",
        amount=amount,
        currency=currency,
        price_history=price_history,
    )
    raw = await _call_gemini(prompt)
    data = _parse_json(raw)
    return PriceAnalysis(**data)


async def generate_insights(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[InsightResponse]:
    """Return stored AI insights for a user, ordered by newest first."""
    result = await db.execute(
        select(AiInsight)
        .where(AiInsight.user_id == user_id)
        .order_by(AiInsight.created_at.desc())
        .limit(20)
    )
    return [InsightResponse.model_validate(i) for i in result.scalars().all()]


async def get_savings_tips(
    spending_breakdown: str,
    currency: str,
) -> list[SavingsTip]:
    prompt = SAVINGS_TIPS_PROMPT.format(
        spending_breakdown=spending_breakdown,
        currency=currency,
    )
    raw = await _call_gemini(prompt)
    data = _parse_json(raw)
    return [SavingsTip(**tip) for tip in data]


async def chat(
    message: str,
    currency: str,
    monthly_income: str = "N/A",
    monthly_expenses: str = "N/A",
) -> ChatResponse:
    system = CHAT_SYSTEM_PROMPT.format(
        currency=currency,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
    )
    prompt = f"{system}\n\nUser: {message}\nAssistant:"
    raw = await _call_gemini(prompt)
    return ChatResponse(reply=raw.strip())
