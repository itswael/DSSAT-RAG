"""Simulation service."""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.simulation import Simulation, SimulationOutput
from app.repositories.simulation import (
    SimulationRepository,
    SimulationOutputRepository,
)
from app.schemas.simulation import (
    SimulationCreate,
    SimulationOutputCreate,
)
from app.services.base import BaseService


class SimulationService(BaseService[Simulation, SimulationCreate, dict]):
    """Service for simulation operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize service.

        Args:
            db: Database session
        """
        self.repository = SimulationRepository(db)
        self.db = db

    async def get_by_experiment_and_run(
        self,
        experiment_name: str,
        run_name: str,
    ) -> Optional[Simulation]:
        """
        Get simulation by experiment name and run name.

        Args:
            experiment_name: Name of the experiment
            run_name: Name of the run

        Returns:
            Simulation record or None
        """
        return await self.repository.get_by_experiment_and_run(
            experiment_name,
            run_name,
        )

    async def get_by_country_state_district(
        self,
        country: str,
        state: Optional[str] = None,
        district: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Simulation]:
        """
        Get simulations by location.

        Args:
            country: Country name
            state: State name (optional)
            district: District name (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of simulation records
        """
        return await self.repository.get_by_country_state_district(
            country,
            state,
            district,
            skip,
            limit,
        )

    async def get_by_crop(
        self,
        crop: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Simulation]:
        """
        Get simulations by crop type.

        Args:
            crop: Crop name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of simulation records
        """
        return await self.repository.get_by_crop(crop, skip, limit)

    async def get_by_year(
        self,
        year: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Simulation]:
        """
        Get simulations by year.

        Args:
            year: Simulation year
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of simulation records
        """
        return await self.repository.get_by_year(year, skip, limit)

    async def get_by_ecological_zone(
        self,
        ecological_zone: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Simulation]:
        """
        Get simulations by ecological zone.

        Args:
            ecological_zone: Ecological zone name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of simulation records
        """
        return await self.repository.get_by_ecological_zone(
            ecological_zone,
            skip,
            limit,
        )

    async def get_within_bbox(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Simulation]:
        """
        Get simulations within bounding box.

        Args:
            min_lat: Minimum latitude
            max_lat: Maximum latitude
            min_lon: Minimum longitude
            max_lon: Maximum longitude
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of simulation records
        """
        return await self.repository.get_within_bbox(
            min_lat,
            max_lat,
            min_lon,
            max_lon,
            skip,
            limit,
        )

    async def get_with_outputs(
        self,
        simulation_id: int,
    ) -> Optional[Simulation]:
        """
        Get simulation with its outputs.

        Args:
            simulation_id: Simulation ID

        Returns:
            Simulation record with outputs loaded
        """
        return await self.repository.get_with_outputs(simulation_id)

    async def create_simulation(
        self,
        simulation_in: SimulationCreate,
    ) -> Simulation:
        """
        Create a new simulation.

        Args:
            simulation_in: Input schema for simulation creation

        Returns:
            Created simulation record
        """
        from app.mappers.simulation import (
            map_simulation_create_to_model,
        )

        # Map schema to model
        simulation = map_simulation_create_to_model(simulation_in)

        # Create in database
        return await self.repository.create(simulation)


class SimulationOutputService(
    BaseService[SimulationOutput, SimulationOutputCreate, dict]
):
    """Service for simulation output operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize service.

        Args:
            db: Database session
        """
        self.repository = SimulationOutputRepository(db)
        self.db = db

    async def get_by_simulation(
        self,
        simulation_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SimulationOutput]:
        """
        Get outputs for a simulation.

        Args:
            simulation_id: Simulation ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of output records
        """
        return await self.repository.get_by_simulation(
            simulation_id,
            skip,
            limit,
        )

    async def get_by_variable(
        self,
        variable_code: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SimulationOutput]:
        """
        Get outputs by variable code.

        Args:
            variable_code: Variable code
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of output records
        """
        return await self.repository.get_by_variable(
            variable_code,
            skip,
            limit,
        )

    async def get_by_simulation_and_variable(
        self,
        simulation_id: int,
        variable_code: str,
    ) -> Optional[SimulationOutput]:
        """
        Get specific output for a simulation.

        Args:
            simulation_id: Simulation ID
            variable_code: Variable code

        Returns:
            Output record or None
        """
        return await self.repository.get_by_simulation_and_variable(
            simulation_id,
            variable_code,
        )

    async def create_output(
        self,
        output_in: SimulationOutputCreate,
        simulation_id: int,
    ) -> SimulationOutput:
        """
        Create a new output for a simulation.

        Args:
            output_in: Input schema for output creation
            simulation_id: Simulation ID

        Returns:
            Created output record
        """
        from app.mappers.simulation import (
            map_output_create_to_model,
        )

        # Map schema to model
        output = map_output_create_to_model(output_in, simulation_id)

        # Create in database
        return await self.repository.create(output)

    async def create_outputs_bulk(
        self,
        outputs_in: list[SimulationOutputCreate],
        simulation_id: int,
    ) -> List[SimulationOutput]:
        """
        Create multiple outputs for a simulation.

        Args:
            outputs_in: List of input schemas for output creation
            simulation_id: Simulation ID

        Returns:
            List of created output records
        """
        from app.mappers.simulation import (
            map_output_create_to_model,
        )

        # Map schemas to models
        outputs = [
            map_output_create_to_model(output_in, simulation_id)
            for output_in in outputs_in
        ]

        # Create in database
        return await self.repository.create_bulk(outputs)
