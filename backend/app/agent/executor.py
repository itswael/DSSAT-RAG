"""Executor - executes tools in parallel based on Planner output.

Refactored for dynamic tool dispatch with asyncio.gather.
Maintains compatibility with legacy QueryPlan.required_tools for now.
"""
import logging
from typing import List, Dict, Any, Optional

import asyncio
from datetime import datetime

from app.agent.models import (
    QueryPlan,
    PlannerOutput,
    PlannerToolCall,
    SimulationToolInput,
    CDEToolInput,
    SemanticToolInput,
    MetadataResult,
    SpatialResult,
    StatisticsResult,
    CDEResult,
    EmbeddingResult,
    ToolError,
    LLMContext
)
from app.services.metadata_service import MetadataService
from app.services.spatial_service import SpatialService
from app.services.statistics_service import StatisticsService
from app.services.cde_service import CDEService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class Executor:
    """Executes tools based on query plan."""
    
    def __init__(self, db_session):
        """
        Initialize executor.
        
        Args:
            db_session: Database session factory/instance
        """
        self.db_session = db_session
    
    async def execute(self, query_plan: QueryPlan, planner_output: Optional[PlannerOutput] = None) -> LLMContext:
        """
        Execute tools based on query plan.
        
        Args:
            query_plan: Generated query plan
            
        Returns:
            Built context for response generation
        """
        start_time = datetime.now()
        timing = {}
        errors = []
        
        # Create services
        db = await self._get_db_session()
        metadata_service = MetadataService(db)
        spatial_service = SpatialService(db)
        statistics_service = StatisticsService(db)
        cde_service = CDEService()
        embedding_service = EmbeddingService()
        
        # If we have a PlannerOutput with explicit tools, use it for dynamic dispatch
        if planner_output and planner_output.tools:
            return await self._execute_from_planner_output(
                db=db,
                planner_output=planner_output,
                timing=timing,
                errors=errors,
            )

        # Dynamic dispatch (legacy): build task list based on inferred required tools
        tasks = []
        task_names = []

        # Legacy mapping: we don't yet store PlannerOutput, so use required_tools
        if "metadata" in query_plan.required_tools:
            tasks.append(self._execute_metadata(metadata_service, query_plan, timing, errors))
            task_names.append("metadata")
        if "spatial" in query_plan.required_tools:
            tasks.append(self._execute_spatial(spatial_service, query_plan, timing, errors))
            task_names.append("spatial")
        if "statistics" in query_plan.required_tools:
            tasks.append(self._execute_statistics(statistics_service, query_plan, timing, errors))
            task_names.append("statistics")
        if "cde" in query_plan.required_tools:
            tasks.append(self._execute_cde(cde_service, query_plan, timing, errors))
            task_names.append("cde")
        if "embedding" in query_plan.required_tools:
            tasks.append(self._execute_embedding(embedding_service, query_plan, timing, errors))
            task_names.append("embedding")

        results = await asyncio.gather(*tasks, return_exceptions=True)

        context_data: Dict[str, Any] = {}
        for i, result in enumerate(results):
            tool_name = task_names[i]
            if isinstance(result, Exception):
                errors.append(ToolError(tool_name=tool_name, error_type=type(result).__name__, message=str(result)))
                logger.error(f"Tool {tool_name} failed: {result}")
            else:
                context_data[tool_name] = result
        
        # Build final context
        llm_context = LLMContext(
            metadata=context_data.get("metadata"),
            spatial=context_data.get("spatial"),
            statistics=context_data.get("statistics"),
            cde=context_data.get("cde"),
            embeddings=context_data.get("embeddings", []),
            query_summary=self._build_query_summary(query_plan, context_data),
            data_quality=self._assess_data_quality(context_data)
        )
        
        # Calculate timing
        total_time = (datetime.now() - start_time).total_seconds()
        timing["total"] = total_time
        
        return llm_context

    async def _execute_from_planner_output(
        self,
        db,
        planner_output: PlannerOutput,
        timing: Dict[str, float],
        errors: List[ToolError],
    ) -> LLMContext:
        start_time = datetime.now()

        # Instantiate tool wrappers
        from app.agent.tools import SimulationTool, CDETool, SemanticTool

        sim_tool = SimulationTool(db)
        cde_tool = CDETool()
        sem_tool = SemanticTool()

        tasks = []
        names: List[str] = []

        for call in planner_output.tools:
            if call.tool == "query_simulation_data":
                tasks.append(sim_tool.run(call.parameters))
                names.append("simulation")
            elif call.tool == "query_cde":
                tasks.append(cde_tool.run(call.parameters))
                names.append("cde")
            elif call.tool == "semantic_search":
                tasks.append(sem_tool.run(call.parameters))
                names.append("semantic")

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map tool outputs to context models
        metadata_res: Optional[MetadataResult] = None
        statistics_res: Optional[StatisticsResult] = None
        cde_res: Optional[CDEResult] = None
        embeddings_res: List[EmbeddingResult] = []

        for i, result in enumerate(results):
            name = names[i]
            if isinstance(result, Exception):
                errors.append(ToolError(tool_name=name, error_type=type(result).__name__, message=str(result)))
                logger.error(f"Tool {name} failed: {result}")
                continue
            if name == "simulation":
                # Build MetadataResult
                sims = result.simulations or []
                metadata_res = MetadataResult(
                    simulations=sims,
                    total_count=len(sims),
                    crops=list({s.get("crop") for s in sims if s.get("crop")}),
                    cultivars=list({s.get("cultivar") for s in sims if s.get("cultivar")}),
                )
                # Build StatisticsResult if present
                if result.statistics and result.statistics.metric:
                    statistics_res = StatisticsResult(
                        aggregation_type=result.statistics.aggregation_type or "",
                        metric=result.statistics.metric or "",
                        value=result.statistics.value,
                        count=result.statistics.count,
                        breakdown=result.statistics.breakdown,
                        unit=result.statistics.unit,
                    )
                timing["query_simulation_data"] = (datetime.now() - start_time).total_seconds()
            elif name == "cde":
                var_defs = []
                for code, d in (result.definitions or {}).items():
                    d = dict(d)
                    d.setdefault("code", code)
                    var_defs.append(d)
                rels = []
                for code, rel in (result.relationships or {}).items():
                    rels.append({"variable": code, "related": rel})
                cde_res = CDEResult(variable_definitions=var_defs, relationships=rels)
                timing["query_cde"] = (datetime.now() - start_time).total_seconds()
            elif name == "semantic":
                docs = result.documents or []
                if docs:
                    embeddings_res.append(EmbeddingResult(
                        documents=[{k: v for k, v in d.items() if k != "score"} for d in docs[:2]],
                        scores=[d.get("score", 0.0) for d in docs[:2]],
                        sources=[d.get("source", "unknown") for d in docs[:2]],
                    ))
                timing["semantic_search"] = (datetime.now() - start_time).total_seconds()

        llm_context = LLMContext(
            metadata=metadata_res,
            spatial=None,
            statistics=statistics_res,
            cde=cde_res,
            embeddings=embeddings_res,
            query_summary=self._build_query_summary(QueryPlan(intent="metadata", filters={}, required_tools=["metadata"], response_type="summary"), {
                "metadata": metadata_res,
                "statistics": statistics_res,
                "cde": cde_res,
                "embeddings": embeddings_res,
            }),
            data_quality=self._assess_data_quality({"metadata": metadata_res, "spatial": None}),
        )
        return llm_context
    
    async def _get_db_session(self):
        """Get database session."""
        # In production, this would get a session from the pool
        # For now, we'll assume it's passed in or create one
        if hasattr(self.db_session, 'session'):
            return await self.db_session.session()
        return self.db_session
    
    async def _execute_metadata(
        self,
        service: MetadataService,
        query_plan: QueryPlan,
        timing: Dict[str, float],
        errors: List[ToolError]
    ) -> Optional[MetadataResult]:
        """Execute metadata tool."""
        start = datetime.now()
        
        try:
            filters = query_plan.filters.copy()
            
            # Remove location from filters (handled by spatial)
            filters.pop("latitude", None)
            filters.pop("longitude", None)
            filters.pop("radius_meters", None)
            
            simulations = await service.get_simulations(**filters)
            
            result = MetadataResult(
                simulations=simulations,
                total_count=len(simulations),
                crops=list(set(s.get("crop") for s in simulations if s.get("crop"))),
                cultivars=list(set(s.get("cultivar") for s in simulations if s.get("cultivar")))
            )
            
            timing["metadata"] = (datetime.now() - start).total_seconds()
            return result
            
        except Exception as e:
            errors.append(ToolError(
                tool_name="metadata",
                error_type=type(e).__name__,
                message=str(e)
            ))
            raise
    
    async def _execute_spatial(
        self,
        service: SpatialService,
        query_plan: QueryPlan,
        timing: Dict[str, float],
        errors: List[ToolError]
    ) -> Optional[SpatialResult]:
        """Execute spatial tool."""
        start = datetime.now()
        
        try:
            if not query_plan.location:
                return None
            
            location = query_plan.location
            filters = query_plan.filters.copy()
            
            simulations = []
            
            if location.type == "radius":
                if location.latitude and location.longitude and location.radius_meters:
                    simulations = await service.search_by_radius(
                        latitude=location.latitude,
                        longitude=location.longitude,
                        radius_meters=location.radius_meters,
                        crop=filters.get("crop")
                    )
            
            elif location.type == "polygon":
                if location.polygon_wkt:
                    simulations = await service.search_by_polygon(
                        polygon_wkt=location.polygon_wkt,
                        crop=filters.get("crop")
                    )
            
            elif location.type == "country":
                if location.country:
                    simulations = await service.search_by_country(
                        country=location.country,
                        state=location.state,
                        district=location.district
                    )
            
            elif location.type in ["state", "district", "ecological_zone"]:
                region_field = location.type
                region_value = getattr(location, region_field)
                if region_value:
                    method = getattr(service, f"search_by_{region_field}")
                    simulations = await method(region_value)
            
            result = SpatialResult(
                simulations=simulations,
                total_count=len(simulations),
                bounds=self._calculate_bounds(simulations)
            )
            
            timing["spatial"] = (datetime.now() - start).total_seconds()
            return result
            
        except Exception as e:
            errors.append(ToolError(
                tool_name="spatial",
                error_type=type(e).__name__,
                message=str(e)
            ))
            raise
    
    async def _execute_statistics(
        self,
        service: StatisticsService,
        query_plan: QueryPlan,
        timing: Dict[str, float],
        errors: List[ToolError]
    ) -> Optional[StatisticsResult]:
        """Execute statistics tool."""
        start = datetime.now()
        
        try:
            if not query_plan.metric or not query_plan.aggregation:
                return None
            
            filters = query_plan.filters.copy()
            
            result = await service.calculate_aggregation(
                variable_code=query_plan.metric,
                aggregation=query_plan.aggregation,
                crop=filters.get("crop"),
                cultivar=filters.get("cultivar"),
                year=filters.get("year")
            )
            
            timing["statistics"] = (datetime.now() - start).total_seconds()
            return StatisticsResult(**result)
            
        except Exception as e:
            errors.append(ToolError(
                tool_name="statistics",
                error_type=type(e).__name__,
                message=str(e)
            ))
            raise
    
    async def _execute_cde(
        self,
        service: CDEService,
        query_plan: QueryPlan,
        timing: Dict[str, float],
        errors: List[ToolError]
    ) -> Optional[CDEResult]:
        """Execute CDE tool."""
        start = datetime.now()
        
        try:
            variable_definitions = []
            
            # Get definitions for relevant variables
            if query_plan.metric:
                definition = await service.get_variable_definition(query_plan.metric)
                if definition:
                    variable_definitions.append(definition)
            
            # Get relationships
            relationships = []
            if query_plan.metric:
                rels = await service.get_variable_relationships(query_plan.metric)
                for rel in rels:
                    defn = await service.get_variable_definition(rel)
                    if defn:
                        relationships.append({
                            "variable": rel,
                            **defn
                        })
            
            # Get cultivar info if cultivar filter exists
            cultivar_info = None
            if query_plan.filters.get("cultivar"):
                crop = query_plan.filters.get("crop", "")
                cultivars = await service.get_cultivar_info(crop)
                for c in cultivars:
                    if c.get("name") == query_plan.filters["cultivar"]:
                        cultivar_info = c
                        break
            
            result = CDEResult(
                variable_definitions=variable_definitions,
                relationships=relationships,
                cultivar_info=cultivar_info
            )
            
            timing["cde"] = (datetime.now() - start).total_seconds()
            return result
            
        except Exception as e:
            errors.append(ToolError(
                tool_name="cde",
                error_type=type(e).__name__,
                message=str(e)
            ))
            raise
    
    async def _execute_embedding(
        self,
        service: EmbeddingService,
        query_plan: QueryPlan,
        timing: Dict[str, float],
        errors: List[ToolError]
    ) -> Optional[List[EmbeddingResult]]:
        """Execute embedding tool."""
        start = datetime.now()
        
        try:
            # Build search query from filters
            search_parts = []
            
            if query_plan.filters.get("crop"):
                search_parts.append(query_plan.filters["crop"])
            if query_plan.filters.get("cultivar"):
                search_parts.append(query_plan.filters["cultivar"])
            if query_plan.location and query_plan.location.country:
                search_parts.append(query_plan.location.country)
            
            search_query = " ".join(search_parts) if search_parts else "DSSAT simulation"
            
            # Search in all collections
            results = []
            
            for collection in ["manuals", "papers", "summaries"]:
                try:
                    docs = await service.search_similar(
                        query=search_query,
                        collection=collection,
                        top_k=3
                    )
                    
                    if docs:
                        results.append(EmbeddingResult(
                            documents=[
                                {"id": d["id"], **d.get("payload", {})}
                                for d in docs[:2]
                            ],
                            scores=[d["score"] for d in docs[:2]],
                            sources=[collection] * min(2, len(docs))
                        ))
                except Exception as e:
                    logger.warning(f"Embedding search failed for {collection}: {e}")
            
            timing["embedding"] = (datetime.now() - start).total_seconds()
            return results
            
        except Exception as e:
            errors.append(ToolError(
                tool_name="embedding",
                error_type=type(e).__name__,
                message=str(e)
            ))
            raise
    
    def _calculate_bounds(self, simulations: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate bounding box from simulations."""
        if not simulations:
            return {"min_lat": 0, "max_lat": 0, "min_lon": 0, "max_lon": 0}
        
        lats = [s.get("latitude", 0) for s in simulations]
        lons = [s.get("longitude", 0) for s in simulations]
        
        return {
            "min_lat": min(lats),
            "max_lat": max(lats),
            "min_lon": min(lons),
            "max_lon": max(lons)
        }
    
    def _build_query_summary(
        self,
        query_plan: QueryPlan,
        context_data: Dict[str, Any]
    ) -> str:
        """Build natural language summary of query results."""
        parts = []
        
        # Intent
        intent_map = {
            "metadata": "Found",
            "aggregate": "Calculated",
            "spatial_search": "Located",
            "comparison": "Compared",
            "trend": "Analyzed trend for"
        }
        
        if query_plan.intent in intent_map:
            parts.append(intent_map[query_plan.intent])
        
        # Filters
        filters = []
        if query_plan.filters.get("crop"):
            filters.append(f"{query_plan.filters['crop']}")
        if query_plan.filters.get("year"):
            filters.append(f"year {query_plan.filters['year']}")
        if query_plan.filters.get("cultivar"):
            filters.append(query_plan.filters["cultivar"])
        
        if filters:
            parts.append(f"for {' '.join(filters)}")
        
        # Location
        if query_plan.location:
            loc_parts = []
            if query_plan.location.country:
                loc_parts.append(query_plan.location.country)
            if query_plan.location.state:
                loc_parts.append(query_plan.location.state)
            
            if loc_parts:
                parts.append(f"in {' '.join(loc_parts)}")
        
        # Results
        result_counts = []
        if context_data.get("metadata"):
            count = context_data["metadata"].total_count
            result_counts.append(f"{count} simulations")
        if context_data.get("spatial"):
            count = context_data["spatial"].total_count
            result_counts.append(f"{count} spatial matches")
        
        if result_counts:
            parts.append(f"({', '.join(result_counts)})")
        
        return " ".join(parts) if parts else "Query executed successfully"
    
    def _assess_data_quality(self, context_data: Dict[str, Any]) -> str:
        """Assess data quality based on results."""
        # Check for sufficient data
        metadata_count = 0
        spatial_count = 0
        
        if context_data.get("metadata"):
            metadata_count = context_data["metadata"].total_count
        if context_data.get("spatial"):
            spatial_count = context_data["spatial"].total_count
        
        total = max(metadata_count, spatial_count)
        
        if total >= 10:
            return "high"
        elif total >= 3:
            return "medium"
        else:
            return "low"
