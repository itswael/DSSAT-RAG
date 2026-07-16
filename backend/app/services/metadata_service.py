"""Metadata Service - retrieves simulation records and basic information."""
import logging
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.simulation import Simulation, SimulationOutput
from app.repositories.simulation import SimulationRepository, SimulationOutputRepository

logger = logging.getLogger(__name__)


class MetadataService:
    """Service for metadata retrieval."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.sim_repo = SimulationRepository(db)
        self.output_repo = SimulationOutputRepository(db)
    
    async def get_simulations(
        self,
        crop: Optional[str] = None,
        cultivar: Optional[str] = None,
        year: Optional[object] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        country: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get simulations with filters.
        
        Args:
            crop: Crop type (optional)
            cultivar: Cultivar name (optional)
            year: Simulation year (optional)
            state: State name (optional)
            district: District name (optional)
            country: Country name (optional)
            limit: Maximum results
            
        Returns:
            List of simulation records as dictionaries
        """
        # Normalize multi-year strings like "2015,2016" to a list of ints
        if isinstance(year, str) and "," in year:
            try:
                year = [int(y.strip()) for y in year.split(",") if y.strip()]
            except Exception:
                pass

        filters = {
            "crop": crop,
            "cultivar": cultivar,
            "year": year,
            "state": state,
            "district": district,
            "country": country
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        logger.info(f"MetadataService.get_simulations filters={filters}")
        simulations = await self.sim_repo.get_with_filters(
            skip=0,
            limit=limit,
            **filters
        )
        
        records = [self._simulation_to_dict(sim) for sim in simulations]
        logger.info(f"MetadataService.get_simulations returned {len(records)} records")
        return records
    
    async def get_simulation_by_id(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get single simulation by ID.
        
        Args:
            simulation_id: Simulation UUID
            
        Returns:
            Simulation record or None
        """
        from uuid import UUID
        
        sim = await self.sim_repo.get(UUID(simulation_id))
        return self._simulation_to_dict(sim) if sim else None
    
    async def get_simulation_outputs(
        self,
        simulation_id: str,
        variable_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get outputs for a simulation.
        
        Args:
            simulation_id: Simulation UUID
            variable_code: Variable filter (optional)
            
        Returns:
            List of output records
        """
        from uuid import UUID
        
        sim = await self.sim_repo.get(UUID(simulation_id))
        if not sim:
            return []
        
        outputs = await self.output_repo.get_by_simulation(
            simulation_id=sim.simulation_id,
            limit=1000
        )
        
        result = []
        for output in outputs:
            if variable_code is None or output.variable_code == variable_code:
                result.append({
                    "variable_code": output.variable_code,
                    "value": output.value,
                    "unit": output.unit
                })
        
        return result
    
    async def get_unique_values(
        self,
        field: str,
        crop: Optional[str] = None
    ) -> List[str]:
        """
        Get unique values for a field.
        
        Args:
            field: Field name (crop, cultivar, state, etc.)
            crop: Filter by crop (optional)
            
        Returns:
            List of unique values
        """
        from sqlalchemy import func
        
        stmt = select(getattr(Simulation, field)).distinct()
        
        if crop:
            stmt = stmt.where(Simulation.crop == crop)
        
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all() if row[0]]
    
    async def get_crop_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics by crop.
        
        Returns:
            Dictionary with crop statistics
        """
        from sqlalchemy import func
        
        stmt = select(
            Simulation.crop,
            func.count().label("count"),
            func.avg(Simulation.simulation_year).label("avg_year")
        ).group_by(Simulation.crop)
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        return {
            "crops": [
                {"name": row[0], "simulation_count": row[1], "avg_year": row[2]}
                for row in rows
            ]
        }
    
    def _simulation_to_dict(self, sim: Simulation) -> Dict[str, Any]:
        """
        Convert simulation model to dictionary.
        
        Args:
            sim: Simulation ORM instance
            
        Returns:
            Dictionary representation
        """
        return {
            "simulation_id": str(sim.simulation_id),
            "experiment_name": sim.experiment_name,
            "run_name": sim.run_name,
            "country": sim.country,
            "state": sim.state,
            "district": sim.district,
            "ecological_zone": sim.ecological_zone,
            "latitude": sim.latitude,
            "longitude": sim.longitude,
            "crop": sim.crop,
            "cultivar": sim.cultivar,
            "irrigation": sim.irrigation,
            "nitrogen_level": sim.nitrogen_level,
            "planting_date": str(sim.planting_date) if sim.planting_date else None,
            "maturity_date": str(sim.maturity_date) if getattr(sim, 'maturity_date', None) else None,
            "harvest_date": str(sim.harvest_date) if sim.harvest_date else None,
            "simulation_year": sim.simulation_year
        }
