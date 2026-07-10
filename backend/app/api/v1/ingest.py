"""Ingestion endpoint."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.ingestion import IngestionService, IngestionResult
from app.parsers.csv_parser import DSSATParser, CanonicalSimulationModel

router = APIRouter()


@router.post("/")
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
        Ingestion result with statistics
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
            # Parse CSV using DSSATParser
            canonical_list: List[CanonicalSimulationModel] = DSSATParser.parse_csv(temp_path)

        finally:
            os.unlink(temp_path)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse CSV file: {str(e)}",
        )

    if not canonical_list:
        return {
            "records_processed": 0,
            "records_failed": 0,
            "execution_time_ms": 0.0,
            "simulation_ids": [],
            "errors": ["No valid data found in CSV file"],
        }

    # Create ingestion service and process
    service = IngestionService(db)

    try:
        result: IngestionResult = await service.ingest_canonical_models(canonical_list)

        return {
            "records_processed": result.records_processed,
            "records_failed": result.records_failed,
            "execution_time_ms": round(result.execution_time_ms, 2),
            "simulation_ids": result.simulation_ids,
            "errors": result.errors,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest data: {str(e)}",
        )


@router.post("/batch")
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
        Ingestion result with statistics for each file
    """
    results = []
    service = IngestionService(db)

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
                canonical_list: List[CanonicalSimulationModel] = DSSATParser.parse_csv(temp_path)

            finally:
                os.unlink(temp_path)

            if not canonical_list:
                results.append(
                    {
                        "file": file.filename,
                        "records_processed": 0,
                        "records_failed": 0,
                        "execution_time_ms": 0.0,
                        "simulation_ids": [],
                        "errors": ["No valid data found in CSV file"],
                    }
                )
                continue

            result: IngestionResult = await service.ingest_canonical_models(canonical_list)

            results.append(
                {
                    "file": file.filename,
                    "records_processed": result.records_processed,
                    "records_failed": result.records_failed,
                    "execution_time_ms": round(result.execution_time_ms, 2),
                    "simulation_ids": result.simulation_ids,
                    "errors": result.errors,
                }
            )

        except Exception as e:
            results.append(
                {
                    "file": file.filename,
                    "records_processed": 0,
                    "records_failed": 0,
                    "execution_time_ms": 0.0,
                    "simulation_ids": [],
                    "error": str(e),
                }
            )

    return {"results": results}
