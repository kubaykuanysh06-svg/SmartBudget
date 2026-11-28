"""AI service — Gemini API integration."""

from __future__ import annotations

import json
import uuid
from typing import TypeVar

from fastapi import HTTPException
from google import genai
from google.genai import errors, types
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.models import AiInsight
from src.ai.prompts import (
    CATEGORIZE_PROMPT,
    CHAT_SYSTEM_PROMPT,
    IMAGE_ANALYSIS_PROMPT,
    PRICE_ANALYSIS_PROMPT,
    SAVINGS_TIPS_PROMPT,
)
from src.ai.schemas import (
    CategorizeSuggestion,
    ChatResponse,
    ImageAnalysis,
    ImageAnalysisResponse,
    InsightResponse,
    PriceAnalysis,
    SavingsTip,
)
from src.core.config import settings

# ── Gemini client helper ──────────────────────────────────

_PLACEHOLDER_GEMINI_KEYS = {"", "your-gemini-api-key", "change-me"}
T = TypeVar("T")


async def _call_gemini(
    contents: str | list[types.Part],
    *,
    config: types.GenerateContentConfig | None = None,
) -> str:
    """Call the Gemini API and return the text response."""
    api_key = settings.GEMINI_API_KEY.strip()
    if api_key in _PLACEHOLDER_GEMINI_KEYS:
        raise HTTPException(status_code=503, detail="Gemini API key is not configured")

    try:
        async with genai.Client(api_key=api_key).aio as client:
            response = await client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=config,
            )
    except errors.APIError:
        raise HTTPException(
            status_code=502, detail="Gemini could not answer the request"
        ) from None
    if not response.text:
        raise HTTPException(status_code=502, detail="Gemini returned an empty response")
    return response.text


async def _call_gemini_structured(
    contents: str | list[types.Part],
    schema: type[T] | object,
    *,
    system_instruction: str | None = None,
) -> T:
    """Call Gemini with JSON structured output and validate with Pydantic."""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=schema,
    )
    raw = await _call_gemini(contents, config=config)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    try:
        adapter = TypeAdapter(schema)
        return adapter.validate_json(cleaned)
    except (ValidationError, json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=502, detail="Gemini returned an invalid structured response"
        ) from None


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
    return await _call_gemini_structured(prompt, CategorizeSuggestion)


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
    return await _call_gemini_structured(prompt, PriceAnalysis)


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
    return await _call_gemini_structured(prompt, list[SavingsTip])


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
    config = types.GenerateContentConfig(system_instruction=system)
    raw = await _call_gemini(message, config=config)
    return ChatResponse(reply=raw.strip())


async def analyze_image(data: bytes, mime_type: str, message: str) -> ImageAnalysisResponse:
    parts = [
        types.Part.from_bytes(data=data, mime_type=mime_type),
        types.Part.from_text(text=message.strip() or "Осы фотоны талдап беріңіз."),
    ]
    analysis = await _call_gemini_structured(
        parts, ImageAnalysis, system_instruction=IMAGE_ANALYSIS_PROMPT
    )
    return ImageAnalysisResponse(
        reply=analysis.reply,
        receipt=analysis.receipt,
        receipt_request_id=uuid.uuid4() if analysis.receipt else None,
    )
