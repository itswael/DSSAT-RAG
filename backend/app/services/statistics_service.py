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

    async def get_available_variables(self) -> List[str]:
        """List distinct variable codes present in simulation_outputs."""
        stmt = select(SimulationOutput.variable_code).distinct().order_by(SimulationOutput.variable_code)
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_available_crops(self) -> List[str]:
        """List distinct crops present in simulations."""
        stmt = select(Simulation.crop).distinct().order_by(Simulation.crop)
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    async def resolve_metric_from_text(self, text_query: str) -> Optional[str]:
        """Resolve a variable_code from free text dynamically (no hardcoding)."""
        q = text_query.lower()
        variables = await self.get_available_variables()
        vars_lower = {v.lower(): v for v in variables}
        tokens = [t.strip(" ,.:;()[]{}") for t in q.split()]
        # 1) direct code token match
        for t in tokens:
            if t in vars_lower:
                return vars_lower[t]
        # 2) simple expansions: remove dashes/underscores
        norm = lambda s: s.replace("-", "").replace("_", "")
        vars_norm = {norm(v.lower()): v for v in variables}
        for t in tokens:
            tn = norm(t)
            if tn in vars_norm:
                return vars_norm[tn]
        # 3) light fuzzy: prefix/substring match (codes are short)
        for v in variables:
            lv = v.lower()
            if any(lv in t or t in lv for t in tokens if len(t) >= 3):
                return v
        # 4) CDE enrichment (optional)
        try:
            from app.services.cde_service import CDEService
            cde = CDEService()
            all_defs = await cde.get_all_variables()
            for item in all_defs:
                code = item.get("code")
                hay = " ".join([code or "", item.get("full_name", ""), item.get("description", "")]).lower()
                if any(tok in hay for tok in tokens if len(tok) >= 3):
                    if code in variables:
                        return code
        except Exception:
            pass
        return None

    async def resolve_crop_from_text(self, text_query: str) -> Optional[str]:
        """Resolve crop code from free text using DB-backed values only."""
        q = text_query.lower()
        crops = await self.get_available_crops()
        crop_map = {c.lower(): c for c in crops}
        for word in q.split():
            w = word.strip(" ,.:;()[]{}")
            if w in crop_map:
                return crop_map[w]
        # allow substring match if unique
        candidates = [c for c in crops if c.lower() in q]
        if len(candidates) == 1:
            return candidates[0]
        return None

    async def resolve_crop_code(self, crop_text: str) -> Optional[str]:
        """Resolve a crop code from a user-provided crop text.

        Attempts exact/ci match against DB crop codes, then falls back to a small
        synonym map for common names (kept minimal; DB-first).
        """
        if not crop_text:
            return None
        crops = await self.get_available_crops()
        # exact case-insensitive match
        for c in crops:
            if c.lower() == crop_text.lower():
                return c
        # synonyms map (expand as needed)
        synonyms = {
            "maize": "MZ",
            "corn": "MZ",
        }
        key = crop_text.strip().lower()
        if key in synonyms and synonyms[key] in crops:
            return synonyms[key]
        # fallback: if crop_text starts with any code when letters removed
        norm = lambda s: ''.join(ch for ch in s.lower() if ch.isalpha())
        ntext = norm(crop_text)
        for c in crops:
            if norm(c) == ntext or c.lower() in ntext or ntext in c.lower():
                return c
        return None
    
    async def calculate_aggregation(
        self,
        variable_code: str,
        aggregation: str,
        crop: Optional[str] = None,
        cultivar: Optional[str] = None,
        year: Optional[object] = None,
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
            try:
                from collections.abc import Iterable
                if isinstance(year, Iterable) and not isinstance(year, (str, bytes)):
                    years = list(year)
                    if len(years) > 0:
                        sim_filters.append(Simulation.simulation_year.in_(years))
                else:
                    sim_filters.append(Simulation.simulation_year == year)  # type: ignore[arg-type]
            except Exception:
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
        
        logger.info(f"StatisticsService.calculate_aggregation var={variable_code} agg={aggregation} filters={{'crop': {crop}, 'cultivar': {cultivar}, 'year': {year}, 'state': {state}, 'district': {district}}}")
        result = await self.db.execute(stmt)
        row = result.fetchone()
        logger.info(f"StatisticsService.calculate_aggregation result value={getattr(row, 'value', None)} count={getattr(row, 'count', 0)}")
        
        return {
            "aggregation_type": aggregation,
            "metric": variable_code,
            "value": row.value if row else None,
            "count": row.count if row else 0,
            "unit": None,
        }

    async def get_extremum_simulation(
        self,
        variable_code: str,
        aggregation: str,
        crop: Optional[str] = None,
        cultivar: Optional[str] = None,
        year: Optional[object] = None,
        state: Optional[str] = None,
        district: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch the simulation record (and value) corresponding to MIN or MAX.

        Returns a dict with simulation and value fields, or None if not found.
        """
        order_desc = aggregation.upper() == "MAX"

        # Build filters
        sim_filters = []
        if crop is not None:
            sim_filters.append(Simulation.crop == crop)
        if cultivar is not None:
            sim_filters.append(Simulation.cultivar == cultivar)
        if year is not None:
            try:
                from collections.abc import Iterable
                if isinstance(year, Iterable) and not isinstance(year, (str, bytes)):
                    years = list(year)
                    if len(years) > 0:
                        sim_filters.append(Simulation.simulation_year.in_(years))
                else:
                    sim_filters.append(Simulation.simulation_year == year)  # type: ignore[arg-type]
            except Exception:
                sim_filters.append(Simulation.simulation_year == year)
        if state is not None:
            sim_filters.append(Simulation.state == state)
        if district is not None:
            sim_filters.append(Simulation.district == district)

        stmt = (
            select(Simulation, SimulationOutput.value.label("value"))
            .join(Simulation, SimulationOutput.simulation_id == Simulation.simulation_id)
            .where(SimulationOutput.variable_code == variable_code)
        )
        if sim_filters:
            stmt = stmt.where(*sim_filters)
        stmt = stmt.order_by(sql_func.desc(SimulationOutput.value) if order_desc else sql_func.asc(SimulationOutput.value)).limit(1)

        res = await self.db.execute(stmt)
        row = res.fetchone()
        if not row:
            return None
        sim: Simulation = row.Simulation if hasattr(row, "Simulation") else row[0]
        val = row.value if hasattr(row, "value") else row[1]
        return {
            "simulation_id": str(sim.simulation_id),
            "value": val,
            "latitude": sim.latitude,
            "longitude": sim.longitude,
            "country": sim.country,
            "state": sim.state,
            "district": sim.district,
            "year": sim.simulation_year,
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
