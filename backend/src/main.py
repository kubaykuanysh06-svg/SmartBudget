"""FastAPI application entry point for SmartBudget."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.ai.router import router as ai_router
from src.analytics.router import router as analytics_router
from src.auth.router import router as auth_router
from src.budgets.router import router as budgets_router
from src.categories.router import router as categories_router
from src.core.config import settings
from src.deals.router import router as deals_router
from src.deals.shopping_router import router as shopping_router
from src.transactions.receipt_router import router as receipt_router
from src.transactions.router import router as transactions_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup actions (e.g. database connection verification)
    yield
    # Shutdown actions


app = FastAPI(
    title="SmartBudget API",
    description="Intelligent personal budget management and spending optimization API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api
app.include_router(auth_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")
app.include_router(receipt_router, prefix="/api")
app.include_router(budgets_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(deals_router, prefix="/api")
app.include_router(shopping_router, prefix="/api")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "app": "SmartBudget API", "version": "1.0.0"}
