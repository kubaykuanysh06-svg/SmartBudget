"""Auth API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import schemas, services
from src.core.dependencies import get_current_user, get_db
from src.core.exceptions import BadRequest
from src.core.security import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
async def register(body: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user = await services.register(
        db,
        email=body.email,
        password=body.password,
        name=body.name,
        currency=body.currency,
    )
    return user


@router.post("/login", response_model=schemas.TokenResponse)
async def login(body: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    user = await services.authenticate(db, email=body.email, password=body.password)
    return schemas.TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh(body: schemas.RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise BadRequest("Invalid token type")
        user_id = payload["sub"]
        user_uuid = uuid.UUID(user_id)
    except (JWTError, KeyError, ValueError):
        raise BadRequest("Invalid refresh token")

    user = await services.get_user_by_id(db, user_uuid)
    if user is None:
        raise BadRequest("Invalid refresh token")

    return schemas.TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=schemas.UserResponse)
async def me(current_user=Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=schemas.UserResponse)
async def update_me(
    body: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.update_user(
        db, current_user, body.model_dump(exclude_unset=True)
    )
