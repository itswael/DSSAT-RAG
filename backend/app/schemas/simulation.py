"""Pydantic schemas for simulation data."""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SimulationBase(BaseModel):
    """Base schema for simulation data."""

    experiment_name: str = Field(..., description="Name of the experiment")
    run_name: str = Field(..., description="Name of the simulation run")
    country: str = Field(..., description="Country where simulation is located")
    state: str | None = Field(None, description="State or region")
    district: str | None = Field(None, description="District or county")
    ecological_zone: str | None = Field(None, description="Ecological zone classification")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate (WGS84)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate (WGS84)")
    location: str | None = Field(None, description="PostGIS geometry point (SRID 4326)")
    geohash: str | None = Field(None, description="Geohash representation of location")
    crop: str = Field(..., description="Crop type")
    cultivar: str | None = Field(None, description="Cultivar name")
    irrigation: str | None = Field(None, description="Irrigation method")
    nitrogen_level: str | None = Field(None, description="Nitrogen application level")
    planting_stage: str | None = Field(None, description="Planting stage description")
    planting_date: date | None = Field(None, description="Date of planting")
    harvest_date: date | None = Field(None, description="Date of harvest")
    simulation_year: int = Field(..., ge=1900, le=2100, description="Year of simulation")
    harvest_area: float | None = Field(None, ge=0, description="Harvested area in hectares")


class SimulationCreate(SimulationBase):
    """Schema for creating a new simulation."""

    pass


class SimulationOutputBase(BaseModel):
    """Base schema for simulation output data."""

    variable_code: str = Field(..., description="Variable code (e.g., YIELD, LAI, ET)")
    value: float = Field(..., description="Value of the variable")
    unit: str | None = Field(None, description="Unit of measurement")


class SimulationOutputCreate(SimulationOutputBase):
    """Schema for creating a new simulation output."""

    pass


class SimulationOutputResponse(SimulationOutputBase):
    """Schema for simulation output response."""

    id: int
    simulation_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SimulationResponse(SimulationBase):
    """Schema for simulation response."""

    simulation_id: UUID
    created_at: datetime
    updated_at: datetime
    outputs: list[SimulationOutputResponse] | None = Field(default=None, description="List of simulation outputs")

    class Config:
        from_attributes = True


class SimulationListResponse(BaseModel):
    """Schema for simulation list response."""

    total: int
    simulations: list[SimulationResponse]


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: str
    database: str
    qdrant: str | None = None
