"""Main FastAPI application."""
import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.agent.tool_registry import ToolRegistry


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    # Configure logging
    base_level = logging.INFO if settings.DEBUG else logging.WARNING
    logging.basicConfig(level=base_level, format="%(levelname)s: %(message)s")
    # Force INFO for our modules so planner/executor/service logs are visible
    for name in [
        "app",
        "app.agent",
        "app.agent.planner",
        "app.agent.executor",
        "app.services.metadata_service",
        "app.services.statistics_service",
    ]:
        logging.getLogger(name).setLevel(logging.INFO)

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

    @app.on_event("startup")
    async def _warm_tool_capabilities():
        try:
            async with AsyncSessionLocal() as session:
                registry = ToolRegistry(session)
                caps = await registry.load_capabilities()
                logging.getLogger(__name__).info(
                    f"Loaded tool capabilities: simulation metrics={len(caps.get('tools', [])[0].get('supported_metrics', []))}"
                )
        except Exception as e:
            logging.getLogger(__name__).warning(f"Tool capabilities warm-up failed: {e}")

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
