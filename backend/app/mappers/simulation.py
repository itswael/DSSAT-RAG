"""Mappers for simulation data."""
from typing import List

from geoalchemy2 import WKTElement
from sqlalchemy import func

from app.models.simulation import Simulation, SimulationOutput
from app.parsers.csv_parser import CanonicalSimulation


def map_canonical_to_simulation(
    canonical: CanonicalSimulation,
) -> Simulation:
    """
    Map CanonicalSimulation to Simulation ORM model.

    Args:
        canonical: Canonical simulation instance

    Returns:
        Simulation ORM model instance
    """
    # Create geometry point from coordinates
    location_wkt = f"POINT({canonical.location.longitude or 0} {canonical.location.latitude or 0})"
    location_geom = WKTElement(location_wkt, srid=4326)

    return Simulation(
        experiment_name=canonical.simulation.experiment_name,
        run_name=canonical.simulation.run_name,
        country=canonical.location.country or "",
        state=canonical.location.state or "",
        district=canonical.location.district or "",
        ecological_zone=canonical.location.ecological_zone or "",
        latitude=canonical.location.latitude or 0.0,
        longitude=canonical.location.longitude or 0.0,
        location=location_geom,
        geohash=None,  # Can be computed later if needed
        crop=canonical.simulation.crop or "",
        cultivar=canonical.simulation.cultivar or "",
        irrigation=canonical.simulation.irrigation or "",
        nitrogen_level=canonical.simulation.nitrogen_level or "",
        planting_stage=canonical.simulation.planting_stage or "",
        planting_date=None,
        harvest_date=None,
        simulation_year=canonical.simulation.year or 2024,
        harvest_area=canonical.simulation.harvest_area,
    )


def map_canonical_to_simulations(
    canonical_list: List[CanonicalSimulation],
) -> List[Simulation]:
    """
    Map list of CanonicalSimulation to Simulation ORM models.

    Args:
        canonical_list: List of canonical simulation instances

    Returns:
        List of Simulation ORM model instances
    """
    return [map_canonical_to_simulation(c) for c in canonical_list]


def map_canonical_outputs(
    canonical: CanonicalSimulation,
    simulation_id: str,
) -> List[SimulationOutput]:
    """
    Map CanonicalSimulation outputs to SimulationOutput ORM models.

    Args:
        canonical: Canonical simulation instance
        simulation_id: Simulation ID to link outputs

    Returns:
        List of SimulationOutput ORM model instances
    """
    outputs = []

    if not canonical.outputs:
        return outputs

    for variable_code, value in canonical.outputs.items():
        output = SimulationOutput(
            simulation_id=simulation_id,
            variable_code=variable_code,
            value=value,
            unit=None,  # Can be populated later if needed
        )
        outputs.append(output)

    return outputs


def map_canonical_outputs_bulk(
    canonical_list: List[CanonicalSimulation],
    simulation_ids: List[str],
) -> List[SimulationOutput]:
    """
    Map list of CanonicalSimulation outputs to SimulationOutput ORM models.

    Args:
        canonical_list: List of canonical simulation instances
        simulation_ids: List of simulation IDs (same order as canonical_list)

    Returns:
        List of SimulationOutput ORM model instances
    """
    outputs = []

    for canonical, sim_id in zip(canonical_list, simulation_ids):
        output_list = map_canonical_outputs(canonical, sim_id)
        outputs.extend(output_list)

    return outputs


def map_simulation_to_response(
    model: Simulation,
) -> dict:
    """
    Map Simulation ORM to response dictionary.

    Args:
        model: Simulation ORM instance

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
