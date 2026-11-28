"""AI API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai import schemas, services
from src.analytics.services import by_category, summary
from src.categories.services import list_categories
from src.core.dependencies import get_current_user, get_db

router = APIRouter(prefix="/ai", tags=["ai"])
MAX_PHOTO_BYTES = 5 * 1024 * 1024


@router.get("/insights", response_model=list[schemas.InsightResponse])
async def get_insights(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.generate_insights(db, current_user.id)


@router.post("/categorize", response_model=schemas.CategorizeSuggestion)
async def categorize(
    body: schemas.CategorizationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    cats = await list_categories(db, current_user.id)
    cat_names = [c.name for c in cats]
    return await services.auto_categorize(
        body.description, body.merchant, body.amount, cat_names
    )


@router.post("/analyze-price", response_model=schemas.PriceAnalysis)
async def analyze_price(
    body: schemas.PriceAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.analyze_price(
        body.description, body.merchant, body.amount, current_user.currency
    )


@router.post("/chat", response_model=schemas.ChatResponse)
async def chat_endpoint(
    body: schemas.ChatMessage,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = await summary(db, current_user.id)
    return await services.chat(
        body.message,
        current_user.currency,
        str(s.total_income),
        str(s.total_expense),
    )


@router.post("/analyze-image", response_model=schemas.ImageAnalysisResponse)
async def analyze_image(
    image: Annotated[UploadFile, File()],
    message: Annotated[str, Form(max_length=2000)] = "",
    _current_user=Depends(get_current_user),
):
    data = await image.read(MAX_PHOTO_BYTES + 1)
    if len(data) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=413, detail="Photo exceeds 5 MiB")

    if data.startswith(b"\xff\xd8\xff"):
        mime_type = "image/jpeg"
    elif data.startswith(b"\x89PNG\r\n\x1a\n"):
        mime_type = "image/png"
    elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        mime_type = "image/webp"
    else:
        raise HTTPException(status_code=415, detail="Expected a JPEG, PNG, or WebP photo")

    return await services.analyze_image(data, mime_type, message)


@router.get("/savings-tips", response_model=list[schemas.SavingsTip])
async def savings_tips(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    breakdown = await by_category(db, current_user.id)
    breakdown_str = "\n".join(
        f"- {b.category_name or 'Uncategorized'}: {b.total} ({b.percentage}%)"
        for b in breakdown
    )
    return await services.get_savings_tips(breakdown_str, current_user.currency)
