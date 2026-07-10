"""Ingestion service for DSSAT data."""
import time
from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.mappers.simulation import (
    map_canonical_to_simulations,
    map_canonical_outputs_bulk,
)
from app.parsers.csv_parser import CanonicalSimulationModel, DSSATParser
from app.repositories.simulation import SimulationRepository, SimulationOutputRepository


class IngestionResult:
    """Result of an ingestion operation."""

    def __init__(
        self,
        records_processed: int = 0,
        records_failed: int = 0,
        execution_time_ms: float = 0.0,
        simulation_ids: List[str] = None,
        errors: List[str] = None,
    ):
        """
        Initialize ingestion result.

        Args:
            records_processed: Number of records successfully processed
            records_failed: Number of records that failed to process
            execution_time_ms: Total execution time in milliseconds
            simulation_ids: List of created simulation IDs
            errors: List of error messages
        """
        self.records_processed = records_processed
        self.records_failed = records_failed
        self.execution_time_ms = execution_time_ms
        self.simulation_ids = simulation_ids or []
        self.errors = errors or []


class IngestionService:
    """Service for ingesting DSSAT data."""

    def __init__(self, db: AsyncSession):
        """
        Initialize ingestion service.

        Args:
            db: Database session
        """
        self.db = db
        self.simulation_repo = SimulationRepository(db)
        self.output_repo = SimulationOutputRepository(db)

    async def ingest_csv(
        self,
        file_path: str,
    ) -> IngestionResult:
        """
        Ingest a DSSAT summary CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            IngestionResult with processing statistics
        """
        start_time = time.time()

        try:
            # Step 1: Parse CSV
            canonical_list = DSSATParser.parse_csv(file_path)

            if not canonical_list:
                return IngestionResult(
                    records_processed=0,
                    records_failed=0,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    errors=["No valid data found in CSV file"],
                )

            # Step 2: Map to ORM models
            simulations = map_canonical_to_simulations(canonical_list)

            # Step 3: Create simulations (bulk insert)
            created_simulations = await self.simulation_repo.create_bulk(simulations)

            # Step 4: Extract simulation IDs in order
            simulation_ids = [str(sim.simulation_id) for sim in created_simulations]

            # Step 5: Map outputs to ORM models
            outputs = map_canonical_outputs_bulk(canonical_list, simulation_ids)

            if outputs:
                # Step 6: Create outputs (bulk insert)
                await self.output_repo.create_bulk(outputs)

            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000

            return IngestionResult(
                records_processed=len(canonical_list),
                records_failed=0,
                execution_time_ms=execution_time_ms,
                simulation_ids=simulation_ids,
            )

        except Exception as e:
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000

            # Rollback on failure
            await self.db.rollback()

            return IngestionResult(
                records_processed=0,
                records_failed=len(canonical_list) if 'canonical_list' in locals() else 0,
                execution_time_ms=execution_time_ms,
                errors=[str(e)],
            )

    async def ingest_canonical_models(
        self,
        canonical_list: List[CanonicalSimulationModel],
    ) -> IngestionResult:
        """
        Ingest a list of canonical simulation models.

        Args:
            canonical_list: List of CanonicalSimulationModel instances

        Returns:
            IngestionResult with processing statistics
        """
        start_time = time.time()

        try:
            if not canonical_list:
                return IngestionResult(
                    records_processed=0,
                    records_failed=0,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    errors=["No data provided"],
                )

            # Step 1: Map to ORM models
            simulations = map_canonical_to_simulations(canonical_list)

            # Step 2: Create simulations (bulk insert)
            created_simulations = await self.simulation_repo.create_bulk(simulations)

            # Step 3: Extract simulation IDs in order
            simulation_ids = [str(sim.simulation_id) for sim in created_simulations]

            # Step 4: Map outputs to ORM models
            outputs = map_canonical_outputs_bulk(canonical_list, simulation_ids)

            if outputs:
                # Step 5: Create outputs (bulk insert)
                await self.output_repo.create_bulk(outputs)

            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000

            return IngestionResult(
                records_processed=len(canonical_list),
                records_failed=0,
                execution_time_ms=execution_time_ms,
                simulation_ids=simulation_ids,
            )

        except Exception as e:
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000

            # Rollback on failure
            await self.db.rollback()

            return IngestionResult(
                records_processed=0,
                records_failed=len(canonical_list),
                execution_time_ms=execution_time_ms,
                errors=[str(e)],
            )
