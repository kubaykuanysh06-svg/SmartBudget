"""Interfaces for store lookup and price comparison."""

from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_user, get_db
from src.deals import comparison, locations
from src.transactions.receipt_insights import product_from_item

router = APIRouter(prefix="/shopping", tags=["shopping"])
Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]


class Position(BaseModel):
    lat: Latitude
    lon: Longitude


class Area(Position):
    radius: float = Field(3, ge=0.5, le=15)


class RouteRequest(Position):
    to_lat: Latitude
    to_lon: Longitude


class ProductQuery(BaseModel):
    name: str = Field("", max_length=255)
    brand: str = Field("", max_length=120)
    barcode: str = Field("", max_length=24)
    variant: str = Field("", max_length=120)
    fat_percent: str = Field("", max_length=12)
    package_size: str = Field("", max_length=20)
    package_unit: str = Field("", max_length=24)


class SearchRequest(BaseModel):
    query: str = Field("", max_length=255)
    reference: ProductQuery | None = None
    area: Area | None = None
    cost_per_km: Decimal = Field(0, ge=0, le=100000, decimal_places=2, allow_inf_nan=False)
    allow_conditions: bool = False


@router.get("/places")
async def search_places(
    query: str = Query(min_length=2, max_length=160),
    lang: Literal["kk", "ru", "en"] = "kk", _=Depends(get_current_user),
):
    return await locations.places(query.strip(), lang)


@router.post("/branches")
async def find_branches(body: Area, _=Depends(get_current_user)):
    return await locations.nearby(body.lat, body.lon, body.radius)


@router.post("/route")
async def get_route(body: RouteRequest, _=Depends(get_current_user)):
    return await locations.route(body.lat, body.lon, body.to_lat, body.to_lon)


@router.post("/compare")
async def compare_prices(body: SearchRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    area = body.area
    branches = (await locations.nearby(area.lat, area.lon, area.radius))["branches"] if area else []
    return await comparison.compare(
        db, user.id, body.query, product_from_item(body.reference.model_dump()) if body.reference else None,
        area.lat if area else None, area.lon if area else None, area.radius if area else 0,
        body.cost_per_km, body.allow_conditions, branches,
    )
