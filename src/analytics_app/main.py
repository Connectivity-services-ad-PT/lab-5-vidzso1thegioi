import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

SERVICE_NAME = os.getenv("SERVICE_NAME", "analytics-service")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.5.0")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "local-dev-token")

app = FastAPI(
    title="FIT4110 Lab 05 - Analytics Service",
    version=SERVICE_VERSION,
    description="Analytics service chạy trong Docker Compose stack cho Lab 05.",
)


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int = Field(..., ge=400, le=599)
    detail: str
    instance: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


def build_problem(*, status_code, title, detail, instance=None):
    p = {"type": "about:blank", "title": title, "status": status_code, "detail": detail}
    if instance:
        p["instance"] = instance
    return p


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail,
                            media_type="application/problem+json")
    return JSONResponse(
        status_code=exc.status_code,
        content=build_problem(status_code=exc.status_code, title="HTTP Error",
                               detail=str(exc.detail), instance=str(request.url.path)),
        media_type="application/problem+json",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=build_problem(status_code=422, title="Validation error",
                               detail="Request validation failed", instance=str(request.url.path)),
        media_type="application/problem+json",
    )


def verify_bearer_token(authorization: Optional[str] = Header(default=None)) -> None:
    if not authorization or authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(
            status_code=401,
            detail=build_problem(status_code=401, title="Unauthorized",
                                  detail="Missing or invalid bearer token"),
        )


# ── Dữ liệu mẫu (in-memory, đủ để test) ──────────────────────────────────────

STATS = {
    "totalReadings": 42,
    "avgTemperature": 31.5,
    "avgHumidity": 65.2,
    "alertCount": 3,
    "generatedAt": "2026-06-14T08:00:00Z",
}

EVENTS = [
    {"eventId": "e001", "type": "telemetry.ingested", "zone": "ZONE-A", "ts": "2026-06-14T07:00:00Z"},
    {"eventId": "e002", "type": "camera.motion.detected", "zone": "ZONE-B", "ts": "2026-06-14T07:05:00Z"},
    {"eventId": "e003", "type": "access.log.created", "zone": "ZONE-A", "ts": "2026-06-14T07:10:00Z"},
]

ALERTS = [
    {"alertId": "a001", "severity": "high", "message": "Temperature spike in ZONE-A", "ts": "2026-06-14T07:15:00Z"},
]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service=SERVICE_NAME, version=SERVICE_VERSION)


@app.head("/health")
def health_head():
    return None


@app.get("/analytics/summary", dependencies=[Depends(verify_bearer_token)])
def get_summary():
    """Trả về thống kê tổng hợp từ dữ liệu cảm biến."""
    return STATS


@app.get("/analytics/events", dependencies=[Depends(verify_bearer_token)])
def get_events(limit: int = 10):
    """Trả về danh sách event gần nhất."""
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422,
                            detail=build_problem(status_code=422, title="Invalid limit",
                                                  detail="limit must be between 1 and 100",
                                                  instance="/analytics/events"))
    return {"items": EVENTS[:limit]}


@app.get("/analytics/alerts", dependencies=[Depends(verify_bearer_token)])
def get_alerts():
    """Trả về danh sách alert hiện tại."""
    return {"items": ALERTS}