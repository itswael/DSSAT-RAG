"""Mappers for canonical models to ORM models."""
from typing import List, Dict, Any

from geoalchemy2 import WKTElement

from app.models.canonical import (
    CanonicalSimulation,
    CanonicalCDE,
    CanonicalDocument,
)
from app.models.simulation import Simulation, SimulationOutput


def map_simulation_to_orm(
    canonical: CanonicalSimulation,
) -> Simulation:
    """
    Map CanonicalSimulation to Simulation ORM model.

    Args:
        canonical: Canonical simulation model

    Returns:
        Simulation ORM instance
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
        geohash=None,
        crop=canonical.simulation.crop or "",
        cultivar=canonical.simulation.cultivar or "",
        irrigation=canonical.simulation.irrigation or "",
        nitrogen_level=canonical.simulation.nitrogen_level or "",
        planting_stage=canonical.simulation.planting_stage or "",
        planting_date=canonical.simulation.planting_date,
        maturity_date=canonical.simulation.maturity_date,
        harvest_date=canonical.simulation.harvest_date,
        simulation_year=canonical.simulation.year or 2024,
        harvest_area=canonical.simulation.harvest_area,
    )


def map_outputs_to_orm(
    canonical: CanonicalSimulation,
    simulation_id: str,
) -> List[SimulationOutput]:
    """
    Map outputs from CanonicalSimulation to SimulationOutput ORM models.

    Args:
        canonical: Canonical simulation model
        simulation_id: Simulation ID to link outputs

    Returns:
        List of SimulationOutput ORM instances
    """
    outputs = []

    for variable_code, value in canonical.outputs.items():
        output = SimulationOutput(
            simulation_id=simulation_id,
            variable_code=variable_code,
            value=value,
            unit=None,
        )
        outputs.append(output)

    return outputs


def map_cde_to_attributes(
    cde: CanonicalCDE,
) -> Dict[str, Any]:
    """
    Map CDE entity to attributes dictionary.

    Args:
        cde: Canonical CDE model

    Returns:
        Dictionary of attributes
    """
    return {
        "entity_type": cde.entity_type,
        "code": cde.code,
        **cde.attributes,
    }


def map_document_to_payload(
    document: CanonicalDocument,
) -> Dict[str, Any]:
    """
    Map document to Qdrant payload.

    Args:
        document: Canonical document model

    Returns:
        Dictionary for Qdrant payload
    """
    return {
        "title": document.title,
        "text": document.text,
        "metadata": document.metadata.model_dump(),
        "document_type": document.document_type,
    }
