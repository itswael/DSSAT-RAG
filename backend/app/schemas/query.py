"""Pydantic schemas for query operations."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryFilters(BaseModel):
    """Query filters for simulation retrieval."""

    crop: Optional[str] = Field(None, description="Crop type")
    cultivar: Optional[str] = Field(None, description="Cultivar name")
    year: Optional[int] = Field(None, ge=1900, le=2100, description="Simulation year")
    state: Optional[str] = Field(None, description="State or region")
    district: Optional[str] = Field(None, description="District or county")
    ecological_zone: Optional[str] = Field(None, description="Ecological zone")
    country: Optional[str] = Field(None, description="Country")


class QueryPlan(BaseModel):
    """Query plan for chatbot queries."""

    intent: str = Field(
        ...,
        description="Type of query (aggregate, filter, search)",
    )
    metric: Optional[str] = Field(
        None,
        description="Metric to aggregate (e.g., HWAM, CWAM, PRCP)",
    )
    aggregation: Optional[str] = Field(
        None,
        description="Aggregation function (avg, max, min, sum)",
    )
    filters: QueryFilters = Field(default_factory=QueryFilters, description="Filter criteria")
    radius: Optional[float] = Field(
        None,
        ge=0,
        description="Radius in kilometers for spatial search",
    )
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude for radius search")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude for radius search")


class QueryResult(BaseModel):
    """Query result structure."""

    metric: str
    aggregation: str
    value: float
    count: int
    filters_applied: Dict[str, Any]
    execution_time_ms: float


class ChatResponse(BaseModel):
    """Chat response with query results."""

    message: str = Field(..., description="Response message")
    result: Optional[QueryResult] = Field(None, description="Query result")
    raw_data: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Raw simulation data",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ChatRequest(BaseModel):
    """Chat request from user."""

    message: str = Field(..., description="User query message")
    session_id: Optional[str] = Field(None, description="Session ID for context")
