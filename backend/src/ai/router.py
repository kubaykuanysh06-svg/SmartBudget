"""AI API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai import schemas, services
from src.analytics.services import by_category, summary
from src.categories.services import list_categories
from src.core.dependencies import get_current_user, get_db

router = APIRouter(prefix="/ai", tags=["ai"])


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
