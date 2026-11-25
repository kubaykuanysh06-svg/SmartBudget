"""Auth Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=255)
    currency: str = Field(default="KZT", min_length=3, max_length=3)

    @field_validator("password")
    @classmethod
    def _validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        return value

    @field_validator("currency")
    @classmethod
    def _normalize_currency(cls, value: str) -> str:
        code = value.strip().upper()
        if len(code) != 3 or not code.isalpha():
            raise ValueError("Currency must be a 3-letter ISO code")
        return code


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    currency: str | None = Field(default=None, min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def _normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        code = value.strip().upper()
        if len(code) != 3 or not code.isalpha():
            raise ValueError("Currency must be a 3-letter ISO code")
        return code


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    currency: str
    settings: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
