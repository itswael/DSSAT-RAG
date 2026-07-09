"""Mappers for simulation data."""
from typing import List

from app.models.simulation import Simulation, SimulationOutput
from app.schemas.simulation import (
    SimulationCreate,
    SimulationOutputCreate,
)


def map_simulation_create_to_model(
    schema: SimulationCreate,
) -> Simulation:
    """
    Map SimulationCreate schema to Simulation model.

    Args:
        schema: Input schema

    Returns:
        Simulation model instance
    """
    from geoalchemy2 import Geometry, WKTElement

    # Create geometry point from coordinates
    location_wkt = f"POINT({schema.longitude} {schema.latitude})"
    location_geom = WKTElement(location_wkt, srid=4326)

    return Simulation(
        experiment_name=schema.experiment_name,
        run_name=schema.run_name,
        country=schema.country,
        state=schema.state,
        district=schema.district,
        ecological_zone=schema.ecological_zone,
        latitude=schema.latitude,
        longitude=schema.longitude,
        location=location_geom,
        geohash=schema.geohash,
        crop=schema.crop,
        cultivar=schema.cultivar,
        irrigation=schema.irrigation,
        nitrogen_level=schema.nitrogen_level,
        planting_stage=schema.planting_stage,
        planting_date=schema.planting_date,
        harvest_date=schema.harvest_date,
        simulation_year=schema.simulation_year,
        harvest_area=schema.harvest_area,
    )


def map_simulation_to_response(
    model: Simulation,
) -> dict:
    """
    Map Simulation model to response dictionary.

    Args:
        model: Simulation model instance

    Returns:
        Response dictionary
    """
    from geoalchemy2 import functions as geo_func

    return {
        "simulation_id": str(model.simulation_id),
        "experiment_name": model.experiment_name,
        "run_name": model.run_name,
        "country": model.country,
        "state": model.state,
        "district": model.district,
        "ecological_zone": model.ecological_zone,
        "latitude": model.latitude,
        "longitude": model.longitude,
        "location": geo_func.ST_AsGeoJSON(model.location) if model.location else None,
        "geohash": model.geohash,
        "crop": model.crop,
        "cultivar": model.cultivar,
        "irrigation": model.irrigation,
        "nitrogen_level": model.nitrogen_level,
        "planting_stage": model.planting_stage,
        "planting_date": str(model.planting_date) if model.planting_date else None,
        "harvest_date": str(model.harvest_date) if model.harvest_date else None,
        "simulation_year": model.simulation_year,
        "harvest_area": model.harvest_area,
        "created_at": str(model.created_at),
        "updated_at": str(model.updated_at),
    }


def map_output_create_to_model(
    schema: SimulationOutputCreate,
    simulation_id: str,
) -> SimulationOutput:
    """
    Map SimulationOutputCreate schema to SimulationOutput model.

    Args:
        schema: Input schema
        simulation_id: Simulation ID

    Returns:
        SimulationOutput model instance
    """
    return SimulationOutput(
        simulation_id=simulation_id,
        variable_code=schema.variable_code,
        value=schema.value,
        unit=schema.unit,
    )


def map_output_to_response(model: SimulationOutput) -> dict:
    """
    Map SimulationOutput model to response dictionary.

    Args:
        model: SimulationOutput model instance

    Returns:
        Response dictionary
    """
    return {
        "id": model.id,
        "simulation_id": str(model.simulation_id),
        "variable_code": model.variable_code,
        "value": model.value,
        "unit": model.unit,
        "created_at": str(model.created_at),
        "updated_at": str(model.updated_at),
    }
