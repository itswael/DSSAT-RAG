"""Main FastAPI application."""
import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    # Configure logging level
    log_level = logging.INFO if settings.DEBUG else logging.WARNING
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    # Ensure agent module logs are visible at INFO in non-debug
    logging.getLogger("app").setLevel(log_level)
    logging.getLogger("app.agent").setLevel(log_level)
    logging.getLogger("app.agent.planner").setLevel(log_level)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="DSSAT Simulation Chatbot Backend API",
        debug=settings.DEBUG,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers under /api to match documented paths
    app.include_router(api_router, prefix="/api")

    @app.get("/")
    async def root() -> dict:
        """Root endpoint."""
        return {
            "message": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
        }

    return app


# Create application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
    )
