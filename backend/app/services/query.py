"""Query service for chatbot queries."""
import time
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.simulation import Simulation, SimulationOutput
from app.repositories.simulation import (
    SimulationRepository,
    SimulationOutputRepository,
)
from app.schemas.query import QueryPlan, QueryResult


class QueryService:
    """Service for executing query plans."""

    def __init__(self, db: AsyncSession):
        """
        Initialize query service.

        Args:
            db: Database session
        """
        self.db = db
        self.simulation_repo = SimulationRepository(db)
        self.output_repo = SimulationOutputRepository(db)

    async def execute_plan(
        self,
        plan: QueryPlan,
    ) -> Dict[str, Any]:
        """
        Execute a query plan.

        Args:
            plan: QueryPlan with intent and filters

        Returns:
            Dictionary with results
        """
        start_time = time.time()

        # Route to appropriate handler based on intent
        if plan.intent == "aggregate":
            result = await self._execute_aggregate(plan)
        elif plan.intent == "filter":
            result = await self._execute_filter(plan)
        elif plan.intent == "search":
            result = await self._execute_search(plan)
        else:
            result = {
                "error": f"Unknown intent: {plan.intent}",
                "raw_data": [],
            }

        execution_time_ms = (time.time() - start_time) * 1000
        result["execution_time_ms"] = round(execution_time_ms, 2)

        return result

    async def _execute_aggregate(
        self,
        plan: QueryPlan,
    ) -> Dict[str, Any]:
        """
        Execute aggregate query.

        Args:
            plan: QueryPlan with metric and aggregation

        Returns:
            Dictionary with aggregated result
        """
        if not plan.metric or not plan.aggregation:
            return {
                "error": "Metric and aggregation are required for aggregate queries",
                "raw_data": [],
            }

        # Build filters from query plan
        filters = {}
        if plan.filters.crop:
            filters["crop"] = plan.filters.crop
        if plan.filters.cultivar:
            filters["cultivar"] = plan.filters.cultivar
        if plan.filters.year:
            filters["year"] = plan.filters.year
        if plan.filters.state:
            filters["state"] = plan.filters.state
        if plan.filters.district:
            filters["district"] = plan.filters.district

        # Execute aggregation
        result = await self.simulation_repo.get_aggregate(
            variable_code=plan.metric,
            aggregation=plan.aggregation,
            **filters,
        )

        return {
            "metric": plan.metric,
            "aggregation": plan.aggregation,
            "value": result.get("value"),
            "count": result.get("count", 0),
            "filters_applied": filters,
            "raw_data": [],
        }

    async def _execute_filter(
        self,
        plan: QueryPlan,
    ) -> Dict[str, Any]:
        """
        Execute filter query.

        Args:
            plan: QueryPlan with filters

        Returns:
            Dictionary with filtered results
        """
        # Build filters from query plan
        filters = {}
        if plan.filters.crop:
            filters["crop"] = plan.filters.crop
        if plan.filters.cultivar:
            filters["cultivar"] = plan.filters.cultivar
        if plan.filters.year:
            filters["year"] = plan.filters.year
        if plan.filters.state:
            filters["state"] = plan.filters.state
        if plan.filters.district:
            filters["district"] = plan.filters.district
        if plan.filters.ecological_zone:
            filters["ecological_zone"] = plan.filters.ecological_zone
        if plan.filters.country:
            filters["country"] = plan.filters.country

        # Get simulations with filters
        simulations = await self.simulation_repo.get_with_filters(**filters)

        # Convert to response format
        raw_data = []
        for sim in simulations:
            raw_data.append({
                "simulation_id": str(sim.simulation_id),
                "experiment_name": sim.experiment_name,
                "run_name": sim.run_name,
                "crop": sim.crop,
                "cultivar": sim.cultivar,
                "year": sim.simulation_year,
                "state": sim.state,
                "district": sim.district,
                "latitude": sim.latitude,
                "longitude": sim.longitude,
            })

        return {
            "filters_applied": filters,
            "count": len(raw_data),
            "raw_data": raw_data,
        }

    async def _execute_search(
        self,
        plan: QueryPlan,
    ) -> Dict[str, Any]:
        """
        Execute search query (radius or polygon).

        Args:
            plan: QueryPlan with radius or polygon

        Returns:
            Dictionary with search results
        """
        raw_data = []

        # Radius search
        if plan.radius and plan.latitude is not None and plan.longitude is not None:
            simulations = await self.simulation_repo.get_within_radius(
                latitude=plan.latitude,
                longitude=plan.longitude,
                radius_km=plan.radius,
            )

            for sim in simulations:
                raw_data.append({
                    "simulation_id": str(sim.simulation_id),
                    "experiment_name": sim.experiment_name,
                    "run_name": sim.run_name,
                    "crop": sim.crop,
                    "cultivar": sim.cultivar,
                    "year": sim.simulation_year,
                    "state": sim.state,
                    "district": sim.district,
                    "latitude": sim.latitude,
                    "longitude": sim.longitude,
                })

        # Polygon search
        elif plan.filters.country or plan.filters.state:
            # Use country/state as polygon filter
            simulations = await self.simulation_repo.get_with_filters(
                country=plan.filters.country,
                state=plan.filters.state,
            )

            for sim in simulations:
                raw_data.append({
                    "simulation_id": str(sim.simulation_id),
                    "experiment_name": sim.experiment_name,
                    "run_name": sim.run_name,
                    "crop": sim.crop,
                    "cultivar": sim.cultivar,
                    "year": sim.simulation_year,
                    "state": sim.state,
                    "district": sim.district,
                    "latitude": sim.latitude,
                    "longitude": sim.longitude,
                })

        return {
            "filters_applied": plan.filters.model_dump(),
            "count": len(raw_data),
            "raw_data": raw_data,
        }

    async def get_simulation_outputs(
        self,
        simulation_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get outputs for a simulation.

        Args:
            simulation_id: Simulation ID

        Returns:
            List of output records
        """
        from uuid import UUID

        try:
            sim_uuid = UUID(simulation_id)
        except ValueError:
            return []

        outputs = await self.output_repo.get_by_simulation(sim_uuid)

        return [
            {
                "variable_code": o.variable_code,
                "value": o.value,
                "unit": o.unit,
            }
            for o in outputs
        ]

    async def get_simulations_with_outputs(
        self,
        crop: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get simulations with their outputs.

        Args:
            crop: Crop type filter (optional)
            year: Year filter (optional)
            limit: Maximum number of results

        Returns:
            List of simulations with outputs
        """
        filters = {}
        if crop:
            filters["crop"] = crop
        if year:
            filters["year"] = year

        simulations = await self.simulation_repo.get_with_filters(**filters, limit=limit)

        result = []
        for sim in simulations:
            outputs = await self.output_repo.get_by_simulation(sim.simulation_id)
            result.append({
                "simulation": {
                    "id": str(sim.simulation_id),
                    "experiment_name": sim.experiment_name,
                    "run_name": sim.run_name,
                    "crop": sim.crop,
                    "year": sim.simulation_year,
                },
                "outputs": [
                    {"variable_code": o.variable_code, "value": o.value}
                    for o in outputs
                ],
            })

        return result
