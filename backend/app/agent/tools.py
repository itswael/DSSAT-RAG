"""Tool wrappers mapping planner tool calls to internal services.

These tools encapsulate business logic and data access; the LLM never sees SQL or schemas.
"""
from __future__ import annotations
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.models import (
    SimulationToolInput, SimulationToolOutput, SimulationStatistics,
    CDEToolInput, CDEToolOutput,
    SemanticToolInput, SemanticToolOutput,
)
from app.services.metadata_service import MetadataService
from app.services.spatial_service import SpatialService
from app.services.statistics_service import StatisticsService
from app.services.cde_service import CDEService
from app.services.embedding_service import EmbeddingService


class SimulationTool:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.meta = MetadataService(db)
        self.stats = StatisticsService(db)
        self.spatial = SpatialService(db)

    async def run(self, params: SimulationToolInput) -> SimulationToolOutput:
        filters = params.filters or {}
        # Normalize multi-year strings like "2015,2016" to a list of ints
        y = filters.get("year")
        if isinstance(y, str) and "," in y:
            try:
                filters["year"] = [int(v.strip()) for v in y.split(",") if v.strip()]
            except Exception:
                pass
        # Resolve crop text to database code if needed (e.g., Maize -> MZ)
        if filters.get("crop"):
            try:
                resolved = await self.stats.resolve_crop_code(str(filters["crop"]))
                if resolved:
                    filters["crop"] = resolved
            except Exception:
                pass

        # Fetch simulations: spatial first if provided, else metadata filters
        simulations = []
        if params.spatial and params.spatial.type:
            sp = params.spatial
            if sp.type == "radius" and sp.latitude is not None and sp.longitude is not None and sp.radius_meters:
                simulations = await self.spatial.search_by_radius(
                    latitude=sp.latitude,
                    longitude=sp.longitude,
                    radius_meters=sp.radius_meters,
                    crop=filters.get("crop"),
                )
            elif sp.type == "polygon" and sp.polygon_wkt:
                simulations = await self.spatial.search_by_polygon(
                    polygon_wkt=sp.polygon_wkt,
                    crop=filters.get("crop"),
                )
            elif sp.type == "country" and sp.country:
                simulations = await self.spatial.search_by_country(
                    country=sp.country,
                    state=sp.state,
                    district=sp.district,
                )
            elif sp.type == "state" and sp.state:
                simulations = await self.spatial.search_by_state(sp.state)
            elif sp.type == "district" and sp.district:
                simulations = await self.spatial.search_by_district(sp.district)
            else:
                simulations = await self.meta.get_simulations(**filters)
        else:
            simulations = await self.meta.get_simulations(**filters)

        statistics = None
        # Optional: include extremum location when MIN/MAX requested
        if params.metrics and params.aggregation:
            metric = params.metrics[0]
            agg = params.aggregation
            stat = await self.stats.calculate_aggregation(
                variable_code=metric,
                aggregation=agg,
                crop=filters.get("crop"),
                cultivar=filters.get("cultivar"),
                year=filters.get("year"),
            )
            statistics = SimulationStatistics(**stat)
            if agg in ("MIN", "MAX"):
                try:
                    ext = await self.stats.get_extremum_simulation(
                        variable_code=metric,
                        aggregation=agg,
                        crop=filters.get("crop"),
                        cultivar=filters.get("cultivar"),
                        year=filters.get("year"),
                    )
                    if ext:
                        # attach location into breakdown for rendering
                        statistics.breakdown = {
                            **(statistics.breakdown or {}),
                            "extremum_location": {
                                "latitude": ext.get("latitude"),
                                "longitude": ext.get("longitude"),
                                "country": ext.get("country"),
                                "state": ext.get("state"),
                                "district": ext.get("district"),
                                "year": ext.get("year"),
                                "simulation_id": ext.get("simulation_id"),
                            }
                        }
                except Exception:
                    pass

        return SimulationToolOutput(
            simulations=simulations,
            statistics=statistics,
            metadata={"count": len(simulations)}
        )


class CDETool:
    def __init__(self):
        self.cde = CDEService()

    async def run(self, params: CDEToolInput) -> CDEToolOutput:
        definitions: Dict[str, Any] = {}
        relationships: Dict[str, Any] = {}

        for v in params.variables or []:
            d = await self.cde.get_variable_definition(v)
            if d:
                definitions[v] = d
            rels = await self.cde.get_variable_relationships(v)
            if rels:
                relationships[v] = rels

        # Cultivar info if provided
        # (Kept minimal to stay compatible)
        return CDEToolOutput(definitions=definitions, relationships=relationships)


class SemanticTool:
    def __init__(self):
        self.emb = EmbeddingService()

    async def run(self, params: SemanticToolInput) -> SemanticToolOutput:
        docs = []
        for collection in ["summaries", "manuals", "papers"]:
            try:
                res = await self.emb.search_similar(query=params.query, collection=collection, top_k=params.top_k)
                for d in res[:2]:
                    docs.append({"id": d.get("id"), **d.get("payload", {}), "source": collection, "score": d.get("score")})
            except Exception:
                continue
        return SemanticToolOutput(documents=docs)
