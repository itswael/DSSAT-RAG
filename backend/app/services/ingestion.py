"""Ingestion service for DSSAT data with multi-format support."""
import time
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.parsers.file_detector import FileTypeDetector, detect_file_type
from app.parsers.csv_parser import DSSATParser as CSVParser
from app.parsers.cultivar_parser import parse_cul_file
from app.parsers.species_parser import parse_spe_file
from app.parsers.ecotype_parser import parse_eco_file
from app.parsers.cde_parser import parse_cde_file
from app.parsers.document_parser import parse_document_file

from app.models.canonical import (
    CanonicalSimulation,
    CanonicalCDE,
    CanonicalDocument,
    IngestionResult,
)
from app.mappers.canonical import (
    map_simulation_to_orm,
    map_outputs_to_orm,
)


class IngestionService:
    """Service for ingesting DSSAT data from multiple file types."""

    def __init__(self, db: AsyncSession):
        """
        Initialize ingestion service.

        Args:
            db: Database session
        """
        self.db = db

    async def ingest_file(
        self,
        file_path: str,
        file_name: str = None,
    ) -> IngestionResult:
        """
        Ingest a single file, automatically detecting type and routing to parser.

        Args:
            file_path: Path to the file
            file_name: Optional file name override

        Returns:
            IngestionResult with processing statistics
        """
        start_time = time.time()

        # Detect file type
        file_type = detect_file_type(file_path)

        if not file_type:
            return IngestionResult(
                file_name=file_name or file_path,
                file_type="unknown",
                records_failed=1,
                errors=["Unsupported file type"],
            )

        result = IngestionResult(
            file_name=file_name or file_path,
            file_type=file_type,
        )

        try:
            # Route to appropriate parser based on file type
            if file_type == "summary_csv":
                canonical_list: List[CanonicalSimulation] = self._parse_summary_csv(file_path)
            elif file_type == "cultivar":
                canonical_list = parse_cul_file(file_path)
            elif file_type == "species":
                canonical_list = parse_spe_file(file_path)
            elif file_type == "ecotype":
                canonical_list = parse_eco_file(file_path)
            elif file_type == "cde":
                cde_entities: List[CanonicalCDE] = parse_cde_file(file_path)
                result.cde_entities = [
                    {"entity_type": e.entity_type, "code": e.code}
                    for e in cde_entities
                ]
                canonical_list = []
            elif file_type == "document":
                document_list: List[CanonicalDocument] = parse_document_file(file_path)
                result.document_ids = [f"doc_{i}" for i in range(len(document_list))]
                canonical_list = []
            else:
                result.errors.append(f"Unknown file type: {file_type}")
                return result

            # Process simulations
            if canonical_list:
                simulation_orms = [
                    map_simulation_to_orm(c) for c in canonical_list
                ]

                # Create simulations in database
                from app.repositories.simulation import SimulationRepository
                sim_repo = SimulationRepository(self.db)
                created_sims = await sim_repo.create_bulk(simulation_orms)

                result.simulation_ids = [str(s.simulation_id) for s in created_sims]

                # Process outputs
                all_outputs = []
                for canonical, simulation in zip(canonical_list, created_sims):
                    outputs = map_outputs_to_orm(canonical, str(simulation.simulation_id))
                    all_outputs.extend(outputs)

                if all_outputs:
                    from app.repositories.simulation import SimulationOutputRepository
                    output_repo = SimulationOutputRepository(self.db)
                    await output_repo.create_bulk(all_outputs)

            result.records_processed = len(canonical_list) + len(result.cde_entities) + len(result.document_ids)

        except Exception as e:
            # Rollback on failure
            await self.db.rollback()
            result.errors.append(str(e))
            result.records_failed = 1

        end_time = time.time()
        result.execution_time_ms = (end_time - start_time) * 1000

        return result

    def _parse_summary_csv(self, file_path: str) -> List[CanonicalSimulation]:
        """
        Parse a summary CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            List of CanonicalSimulation instances
        """
        return CSVParser.parse_csv(file_path)

    async def ingest_files(
        self,
        file_paths: List[str],
    ) -> Dict[str, Any]:
        """
        Ingest multiple files.

        Args:
            file_paths: List of file paths

        Returns:
            Dictionary with batch results
        """
        results = []
        successful = 0
        failed = 0

        for file_path in file_paths:
            try:
                result = await self.ingest_file(file_path)
                if result.records_processed > 0 and not result.errors:
                    successful += 1
                else:
                    failed += 1
                results.append(result)
            except Exception as e:
                results.append(
                    IngestionResult(
                        file_name=file_path,
                        file_type="unknown",
                        records_failed=1,
                        errors=[str(e)],
                    )
                )
                failed += 1

        return {
            "total_files": len(file_paths),
            "successful": successful,
            "failed": failed,
            "results": results,
        }
