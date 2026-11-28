"""Retail locations from OSM-derived providers."""

import asyncio
import math
import os
from time import monotonic

import httpx

HEADERS = {"User-Agent": "SmartBudget/1.0 (interactive retail locator)"}
PHOTON = os.getenv("SMARTBUDGET_GEOCODER_URL", "https://photon.komoot.io/api/")
# Comma-separated; public Overpass servers are often at capacity, so try each in turn.
OVERPASS = [url.strip() for url in os.getenv(
    "SMARTBUDGET_STORES_URL",
    "https://overpass.kumi.systems/api/interpreter,https://overpass-api.de/api/interpreter,"
    "https://overpass.private.coffee/api/interpreter",
).split(",") if url.strip()]
ROUTE_SERVICE = os.getenv("SMARTBUDGET_ROUTE_URL", "").rstrip("/")
CACHE: dict[tuple, tuple[float, object]] = {}
REQUEST_LIMIT = asyncio.Semaphore(2)
CITIES = [
    ("Қызылорда", "Кызылорда", "Kyzylorda", 44.8488, 65.4823),
    ("Алматы", "Алматы", "Almaty", 43.2389, 76.8897),
    ("Астана", "Астана", "Astana", 51.1694, 71.4491),
    ("Шымкент", "Шымкент", "Shymkent", 42.3417, 69.5901),
    ("Ақтөбе", "Актобе", "Aktobe", 50.2839, 57.1669),
    ("Қарағанды", "Караганда", "Karaganda", 49.8060, 73.0850),
    ("Атырау", "Атырау", "Atyrau", 47.0945, 51.9238),
    ("Ақтау", "Актау", "Aktau", 43.6532, 51.1975),
]


def distance_km(lat: float, lon: float, to_lat: float, to_lon: float) -> float:
    scale = math.pi / 180
    a = math.sin((to_lat - lat) * scale / 2) ** 2
    a += math.cos(lat * scale) * math.cos(to_lat * scale) * math.sin((to_lon - lon) * scale / 2) ** 2
    return 12742 * math.asin(min(1.0, math.sqrt(a)))


async def cached_json(key: tuple, ttl: int, method: str, url: str, **options):
    cached = CACHE.get(key)
    if cached and monotonic() - cached[0] < ttl:
        return cached[1]
    async with REQUEST_LIMIT, httpx.AsyncClient(headers=HEADERS, timeout=12) as client:
        response = await client.request(method, url, **options)
        response.raise_for_status()
        body = response.json()
    if len(CACHE) >= 256:
        CACHE.pop(next(iter(CACHE)))
    CACHE[key] = monotonic(), body
    return body


async def places(query: str, lang: str) -> list[dict]:
    results = [
        {"name": {"kk": kk, "ru": ru, "en": en}[lang], "lat": lat, "lon": lon}
        for kk, ru, en, lat, lon in CITIES
        if any(query.casefold() in name.casefold() for name in (kk, ru, en))
    ]
    if any(query.casefold() == name.casefold() for city in CITIES for name in city[:3]):
        return results
    try:
        data = await cached_json(("places", query.casefold(), lang), 3600, "GET", PHOTON,
            params={"q": query, "limit": 7, "lang": lang if lang != "kk" else "en"})
        for feature in data.get("features", []):
            info = feature.get("properties", {})
            if str(info.get("countrycode", "")).upper() != "KZ":
                continue
            lon, lat = feature["geometry"]["coordinates"][:2]
            parts = dict.fromkeys(filter(None, (info.get("name"), info.get("street"), info.get("housenumber"), info.get("city"))))
            results.append({"name": ", ".join(parts), "lat": lat, "lon": lon})
    except (httpx.HTTPError, ValueError, KeyError):
        pass
    return results[:8]


async def nearby(lat: float, lon: float, radius: float) -> dict:
    lat_key, lon_key = round(lat, 3), round(lon, 3)
    meters = round(radius * 1000 + 200)
    query = (f'[out:json][timeout:9];nwr(around:{meters},{lat_key},{lon_key})'
             '["shop"~"^(supermarket|convenience|grocery|discount|mall)$"]["name"];out center 400;')
    data = None
    for url in OVERPASS:
        try:
            data = await cached_json(("stores", lat_key, lon_key, radius), 1800, "POST", url, data={"data": query})
            break
        except (httpx.HTTPError, ValueError):
            continue
    if data is None:
        return {"available": False, "branches": []}
    branches = []
    for entry in data.get("elements", []):
        point = entry.get("center") or entry
        tags = entry.get("tags") or {}
        if "lat" not in point or "lon" not in point:
            continue
        km = distance_km(lat, lon, point["lat"], point["lon"])
        if km > radius:
            continue
        address = " ".join(filter(None, [tags.get("addr:street"), tags.get("addr:housenumber")]))
        branches.append({
            "id": f'{entry["type"]}/{entry["id"]}', "name": tags["name"], "address": address,
            "lat": point["lat"], "lon": point["lon"], "distance_km": round(km, 2),
        })
    return {"available": True, "branches": sorted(branches, key=lambda row: row["distance_km"])[:100]}


async def route(lat: float, lon: float, to_lat: float, to_lon: float) -> dict | None:
    if not ROUTE_SERVICE:
        return None
    points = f"{lon:.5f},{lat:.5f};{to_lon:.5f},{to_lat:.5f}"
    try:
        data = await cached_json(("route", points), 300, "GET",
            f"{ROUTE_SERVICE}/route/v1/driving/{points}", params={"overview": "false"})
        best = next(iter(data.get("routes", [])), None)
        if best:
            return {"distance_km": round(best["distance"] / 1000, 2), "minutes": round(best["duration"] / 60)}
    except (httpx.HTTPError, ValueError, KeyError):
        pass
    return None
