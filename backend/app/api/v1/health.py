"""Health check endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()


@router.get("/status")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Health check endpoint.

    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "database": "connected",
    }


@router.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "DSSAT RAG Backend API"}
