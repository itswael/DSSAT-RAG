"""Simulation repository."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.simulation import Simulation, SimulationOutput
from app.repositories.base import BaseRepository


class SimulationRepository(BaseRepository[Simulation]):
    """Repository for simulation operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository.

        Args:
            db: Database session
        """
        super().__init__(Simulation, db)

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
        stmt = (
            select(Simulation)
            .where(
                Simulation.experiment_name == experiment_name,
                Simulation.run_name == run_name,
            )
            .options(selectinload(Simulation.outputs))
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

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
        stmt = select(Simulation).where(Simulation.country == country).offset(skip).limit(limit)

        if state:
            stmt = stmt.where(Simulation.state == state)

        if district:
            stmt = stmt.where(Simulation.district == district)

        result = await self.db.execute(stmt)
        return result.scalars().all()

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
        stmt = (
            select(Simulation)
            .where(Simulation.crop == crop)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

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
        stmt = (
            select(Simulation)
            .where(Simulation.simulation_year == year)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

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
        stmt = (
            select(Simulation)
            .where(Simulation.ecological_zone == ecological_zone)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

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
        from geoalchemy2 import functions as geo_func
        from sqlalchemy import and_

        stmt = (
            select(Simulation)
            .where(
                and_(
                    Simulation.latitude >= min_lat,
                    Simulation.latitude <= max_lat,
                    Simulation.longitude >= min_lon,
                    Simulation.longitude <= max_lon,
                )
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_with_outputs(
        self,
        simulation_id: UUID,
    ) -> Optional[Simulation]:
        """
        Get simulation with its outputs.

        Args:
            simulation_id: Simulation ID

        Returns:
            Simulation record with outputs loaded
        """
        stmt = (
            select(Simulation)
            .where(Simulation.simulation_id == simulation_id)
            .options(selectinload(Simulation.outputs))
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class SimulationOutputRepository(BaseRepository[SimulationOutput]):
    """Repository for simulation output operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository.

        Args:
            db: Database session
        """
        super().__init__(SimulationOutput, db)

    async def get_by_simulation(
        self,
        simulation_id: UUID,
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
        stmt = (
            select(SimulationOutput)
            .where(SimulationOutput.simulation_id == simulation_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

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
        stmt = (
            select(SimulationOutput)
            .where(SimulationOutput.variable_code == variable_code)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_simulation_and_variable(
        self,
        simulation_id: UUID,
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
        stmt = (
            select(SimulationOutput)
            .where(
                SimulationOutput.simulation_id == simulation_id,
                SimulationOutput.variable_code == variable_code,
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
