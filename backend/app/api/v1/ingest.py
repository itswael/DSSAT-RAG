"""Ingestion endpoint."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.simulation import Simulation
from app.repositories.simulation import SimulationRepository
from app.schemas.simulation import (
    SimulationCreate,
    SimulationResponse,
)
from app.services.simulation import SimulationService
from app.parsers.csv_parser import CSVParser, parse_summary_csv

router = APIRouter()


@router.post("/", response_model=SimulationResponse)
async def ingest_simulation(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Ingest a DSSAT summary CSV file.

    Args:
        file: Uploaded CSV file
        db: Database session

    Returns:
        Ingestion result with simulation ID
    """
    # Parse the CSV file
    try:
        content = await file.read()
        csv_content = content.decode("utf-8")

        # Write to temporary file for parsing
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
        ) as tmp_file:
            tmp_file.write(csv_content)
            temp_path = tmp_file.name

        try:
            data = parse_summary_csv(temp_path)
        finally:
            os.unlink(temp_path)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse CSV file: {str(e)}",
        )

    if not data:
        raise HTTPException(
            status_code=400,
            detail="No data found in CSV file",
        )

    # Extract simulation metadata from first row
    # Note: This is a simplified example - adjust based on actual CSV structure
    first_row = data[0]

    try:
        simulation_in = SimulationCreate(
            experiment_name=first_row.get("EXPNAME", "Unknown"),
            run_name=first_row.get("RUNNAME", "Unknown"),
            country=first_row.get("COUNTRY", ""),
            state=first_row.get("STATE", ""),
            district=first_row.get("DISTRICT", ""),
            ecological_zone=first_row.get("ECOZONE", ""),
            latitude=float(first_row.get("LATITUDE", 0)),
            longitude=float(first_row.get("LONGITUDE", 0)),
            crop=first_row.get("CROP", ""),
            simulation_year=int(first_row.get("YEAR", 2024)),
        )

    except (ValueError, KeyError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV data: {str(e)}",
        )

    # Create service and save simulation
    service = SimulationService(db)
    simulation = await service.create_simulation(simulation_in)

    return {
        "message": "Simulation ingested successfully",
        "simulation_id": str(simulation.simulation_id),
    }


@router.post("/batch", response_model=List[SimulationResponse])
async def ingest_simulations_batch(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Ingest multiple DSSAT summary CSV files.

    Args:
        files: Uploaded CSV files
        db: Database session

    Returns:
        Ingestion result with simulation IDs
    """
    results = []
    service = SimulationService(db)

    for file in files:
        try:
            content = await file.read()
            csv_content = content.decode("utf-8")

            import tempfile
            import os

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".csv",
                delete=False,
            ) as tmp_file:
                tmp_file.write(csv_content)
                temp_path = tmp_file.name

            try:
                data = parse_summary_csv(temp_path)
            finally:
                os.unlink(temp_path)

            if not data:
                continue

            first_row = data[0]

            simulation_in = SimulationCreate(
                experiment_name=first_row.get("EXPNAME", "Unknown"),
                run_name=first_row.get("RUNNAME", "Unknown"),
                country=first_row.get("COUNTRY", ""),
                state=first_row.get("STATE", ""),
                district=first_row.get("DISTRICT", ""),
                ecological_zone=first_row.get("ECOZONE", ""),
                latitude=float(first_row.get("LATITUDE", 0)),
                longitude=float(first_row.get("LONGITUDE", 0)),
                crop=first_row.get("CROP", ""),
                simulation_year=int(first_row.get("YEAR", 2024)),
            )

            simulation = await service.create_simulation(simulation_in)

            results.append(
                {
                    "file": file.filename,
                    "simulation_id": str(simulation.simulation_id),
                    "status": "success",
                }
            )

        except Exception as e:
            results.append(
                {
                    "file": file.filename,
                    "error": str(e),
                    "status": "failed",
                }
            )

    return {"results": results}
