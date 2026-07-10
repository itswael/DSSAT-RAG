"""API routes."""
from fastapi import APIRouter

from app.api.v1 import ingest, health

api_router = APIRouter()

# Include versioned routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(ingest.router, prefix="/v1/ingest", tags=["ingestion"])
