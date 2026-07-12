"""Statistics Service - aggregate calculations and statistical analysis."""
import logging
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func as sql_func, text

from app.models.simulation import Simulation, SimulationOutput
from app.repositories.simulation import SimulationRepository, SimulationOutputRepository

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for statistical calculations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.sim_repo = SimulationRepository(db)
        self.output_repo = SimulationOutputRepository(db)
    
    async def calculate_aggregation(
        self,
        variable_code: str,
        aggregation: str,
        crop: Optional[str] = None,
        cultivar: Optional[str] = None,
        year: Optional[int] = None,
        state: Optional[str] = None,
        district: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate aggregate statistics.
        
        Args:
            variable_code: Variable to aggregate (e.g., HWAM, YIELD)
            aggregation: Function (AVG, MIN, MAX, COUNT, SUM)
            crop: Filter by crop (optional)
            cultivar: Filter by cultivar (optional)
            year: Filter by year (optional)
            state: Filter by state (optional)
            district: Filter by district (optional)
            
        Returns:
            Aggregation result
        """
        # Build filters for simulation join
        sim_filters = []
        if crop is not None:
            sim_filters.append(Simulation.crop == crop)
        if cultivar is not None:
            sim_filters.append(Simulation.cultivar == cultivar)
        if year is not None:
            sim_filters.append(Simulation.simulation_year == year)
        if state is not None:
            sim_filters.append(Simulation.state == state)
        if district is not None:
            sim_filters.append(Simulation.district == district)
        
        # Build aggregation query
        agg_func = {
            "avg": sql_func.avg,
            "max": sql_func.max,
            "min": sql_func.min,
            "count": sql_func.count,
            "sum": sql_func.sum,
        }.get(aggregation.lower(), sql_func.avg)
        
        stmt = (
            select(
                agg_func(SimulationOutput.value).label("value"),
                sql_func.count().label("count"),
                sql_func.stddev(SimulationOutput.value).label("stddev")
            )
            .join(Simulation, SimulationOutput.simulation_id == Simulation.simulation_id)
            .where(SimulationOutput.variable_code == variable_code)
        )
        
        if sim_filters:
            stmt = stmt.where(*sim_filters)
        
        result = await self.db.execute(stmt)
        row = result.fetchone()
        
        return {
            "aggregation_type": aggregation,
            "variable_code": variable_code,
            "value": row.value if row else None,
            "count": row.count if row else 0,
            "stddev": row.stddev if row and row.stddev else 0
        }
    
    async def calculate_breakdown(
        self,
        variable_code: str,
        aggregation: str,
        group_by: str,
        crop: Optional[str] = None,
        cultivar: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculate aggregations with breakdown by category.
        
        Args:
            variable_code: Variable to aggregate
            aggregation: Function (AVG, MIN, MAX, COUNT, SUM)
            group_by: Group by field (cultivar, year, state, etc.)
            crop: Filter by crop (optional)
            cultivar: Filter by cultivar (optional)
            year: Filter by year (optional)
            
        Returns:
            List of breakdown results
        """
        # Build filters
        sim_filters = []
        if crop is not None:
            sim_filters.append(Simulation.crop == crop)
        if cultivar is not None:
            sim_filters.append(Simulation.cultivar == cultivar)
        if year is not None:
            sim_filters.append(Simulation.simulation_year == year)
        
        # Get group field
        group_field = getattr(Simulation, group_by, None)
        if not group_field:
            raise ValueError(f"Invalid group field: {group_by}")
        
        agg_func = {
            "avg": sql_func.avg,
            "max": sql_func.max,
            "min": sql_func.min,
            "count": sql_func.count,
            "sum": sql_func.sum,
        }.get(aggregation.lower(), sql_func.avg)
        
        stmt = (
            select(
                group_field.label("group_value"),
                agg_func(SimulationOutput.value).label("value"),
                sql_func.count().label("count")
            )
            .join(Simulation, SimulationOutput.simulation_id == Simulation.simulation_id)
            .where(SimulationOutput.variable_code == variable_code)
        )
        
        if sim_filters:
            stmt = stmt.where(*sim_filters)
        
        stmt = stmt.group_by(group_field).order_by(sql_func.desc("value"))
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        return [
            {
                "group_value": row.group_value,
                "value": row.value,
                "count": row.count
            }
            for row in rows
        ]
    
    async def get_variable_stats(
        self,
        variable_code: str,
        crop: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a variable.
        
        Args:
            variable_code: Variable code
            crop: Filter by crop (optional)
            
        Returns:
            Statistics dictionary
        """
        # Build filters
        sim_filters = []
        if crop is not None:
            sim_filters.append(Simulation.crop == crop)
        
        stmt = (
            select(
                sql_func.min(SimulationOutput.value).label("min"),
                sql_func.max(SimulationOutput.value).label("max"),
                sql_func.avg(SimulationOutput.value).label("avg"),
                sql_func.stddev(SimulationOutput.value).label("stddev"),
                sql_func.count().label("count")
            )
            .join(Simulation, SimulationOutput.simulation_id == Simulation.simulation_id)
            .where(SimulationOutput.variable_code == variable_code)
        )
        
        if sim_filters:
            stmt = stmt.where(*sim_filters)
        
        result = await self.db.execute(stmt)
        row = result.fetchone()
        
        return {
            "variable_code": variable_code,
            "min": row.min if row else None,
            "max": row.max if row else None,
            "avg": row.avg if row else None,
            "stddev": row.stddev if row and row.stddev else 0,
            "count": row.count if row else 0
        }
    
    async def get_yearly_trend(
        self,
        variable_code: str,
        crop: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get yearly trend data.
        
        Args:
            variable_code: Variable code
            crop: Filter by crop (optional)
            start_year: Start year (optional)
            end_year: End year (optional)
            
        Returns:
            List of yearly averages
        """
        # Build filters
        sim_filters = []
        if crop is not None:
            sim_filters.append(Simulation.crop == crop)
        
        stmt = (
            select(
                Simulation.simulation_year.label("year"),
                sql_func.avg(SimulationOutput.value).label("avg_value"),
                sql_func.count().label("count")
            )
            .join(Simulation, SimulationOutput.simulation_id == Simulation.simulation_id)
            .where(SimulationOutput.variable_code == variable_code)
        )
        
        if sim_filters:
            stmt = stmt.where(*sim_filters)
        
        if start_year is not None:
            stmt = stmt.where(Simulation.simulation_year >= start_year)
        
        if end_year is not None:
            stmt = stmt.where(Simulation.simulation_year <= end_year)
        
        stmt = stmt.group_by(Simulation.simulation_year).order_by(Simulation.simulation_year)
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        return [
            {
                "year": row.year,
                "avg_value": row.avg_value,
                "count": row.count
            }
            for row in rows
        ]
    
    async def get_top_simulations(
        self,
        variable_code: str,
        aggregation: str = "max",
        limit: int = 10,
        crop: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top simulations by variable.
        
        Args:
            variable_code: Variable code
            aggregation: Sort order (max or min)
            limit: Number of results
            crop: Filter by crop (optional)
            
        Returns:
            List of top simulations with their values
        """
        # Build filters
        sim_filters = []
        if crop is not None:
            sim_filters.append(Simulation.crop == crop)
        
        agg_func = sql_func.max if aggregation.lower() == "max" else sql_func.min
        
        stmt = (
            select(
                Simulation,
                agg_func(SimulationOutput.value).label("value")
            )
            .join(SimulationOutput, Simulation.simulation_id == SimulationOutput.simulation_id)
            .where(SimulationOutput.variable_code == variable_code)
        )
        
        if sim_filters:
            stmt = stmt.where(*sim_filters)
        
        stmt = stmt.group_by(Simulation.simulation_id).order_by(sql_func.desc("value")).limit(limit)
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        return [
            {
                "simulation_id": str(row.Simulation.simulation_id),
                "experiment_name": row.Simulation.experiment_name,
                "run_name": row.Simulation.run_name,
                "value": row.value,
                "crop": row.Simulation.crop,
                "cultivar": row.Simulation.cultivar
            }
            for row in rows
        ]
