"""User model."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RUB", nullable=False)
    settings: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────
    transactions = relationship(
        "Transaction", back_populates="user", lazy="selectin"
    )
    categories = relationship("Category", back_populates="user", lazy="selectin")
    budgets = relationship("Budget", back_populates="user", lazy="selectin")
    recurring_transactions = relationship(
        "RecurringTransaction", back_populates="user", lazy="selectin"
    )
    ai_insights = relationship("AiInsight", back_populates="user", lazy="selectin")
    price_histories = relationship(
        "PriceHistory", back_populates="user", lazy="selectin"
    )
