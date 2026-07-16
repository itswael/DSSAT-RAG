"""Agent orchestrator Pydantic models."""
from datetime import date
from typing import Any, Dict, List, Optional, Literal, Union

from pydantic import BaseModel, Field


# =============================================================================
# QUERY PLANNER MODELS
# =============================================================================

class LocationFilter(BaseModel):
    """Location-based filtering criteria."""
    
    type: Literal["radius", "polygon", "country", "state", "district", "ecological_zone"]
    """Type of location filter."""
    
    # For radius search
    latitude: float | None = None
    longitude: float | None = None
    radius_meters: int | None = None
    
    # For polygon search
    polygon_wkt: str | None = None
    
    # For region-based search
    country: str | None = None
    state: str | None = None
    district: str | None = None
    ecological_zone: str | None = None


class QueryPlan(BaseModel):
    """LLM-generated query plan."""
    
    intent: Literal[
        "metadata",
        "aggregate",
        "spatial_search",
        "comparison",
        "trend",
        "explanation",
        "hybrid"
    ]
    """The user's primary intent."""
    
    metric: Optional[str] = None
    """Target metric (e.g., HWAM, YIELD)."""
    
    aggregation: Optional[Literal["AVG", "MIN", "MAX", "COUNT", "SUM"]] = None
    """Aggregation function for aggregate queries."""
    
    filters: Dict[str, Any] = Field(default_factory=dict)
    """Filter criteria (crop, cultivar, year, etc.)."""
    
    location: Optional[LocationFilter] = None
    """Location-based filtering."""
    
    comparison: Optional[Dict[str, List[str]]] = None
    """For comparison queries - groups to compare."""
    
    time_range: Optional[Dict[str, int]] = None
    """Time range for trend analysis."""
    
    required_tools: List[Literal[
        "metadata",
        "spatial",
        "statistics",
        "cde",
        "embedding"
    ]]
    """Tools needed to fulfill this query."""
    
    response_type: Literal["summary", "detailed", "comparison", "trend"] = "summary"
    """Preferred response format."""


# =============================================================================
# EXECUTOR MODELS
# =============================================================================

class MetadataResult(BaseModel):
    """Metadata tool result."""
    
    simulations: List[Dict[str, Any]]
    """Matching simulation records."""
    
    total_count: int
    """Total number of matching simulations."""
    
    crops: List[str]
    """Available crop types in results."""
    
    cultivars: List[str]
    """Available cultivars in results."""
    
    years: List[int] = []
    """Years covered by results."""


class SpatialResult(BaseModel):
    """Spatial tool result."""
    
    simulations: List[Dict[str, Any]]
    """Simulations within spatial filter."""
    
    total_count: int
    """Total matching count."""
    
    bounds: Dict[str, float]
    """Bounding box of results."""
    
    distance_stats: Optional[Dict[str, float]] = None
    """Distance statistics for radius searches."""


class StatisticsResult(BaseModel):
    """Statistics tool result."""
    
    aggregation_type: str
    """Type of aggregation performed."""
    
    metric: str
    """Target metric."""
    
    value: Optional[float]
    """Aggregated value."""
    
    count: int
    """Number of records aggregated."""
    
    breakdown: Optional[Dict[str, Any]] = None
    """Breakdown by groups (e.g., cultivar, year)."""
    
    unit: Optional[str] = None
    """Unit of measurement."""


class CDEResult(BaseModel):
    """CDE tool result."""
    
    variable_definitions: List[Dict[str, str]]
    """Variable code to definition mappings."""
    
    relationships: List[Dict[str, Any]]
    """Variable relationships."""
    
    cultivar_info: Optional[Dict[str, Any]] = None
    """Cultivar-specific information."""
    
    species_info: Optional[Dict[str, Any]] = None
    """Species-specific information."""


class EmbeddingResult(BaseModel):
    """Embedding tool result."""
    
    documents: List[Dict[str, Any]]
    """Relevant documents and summaries."""
    
    scores: List[float]
    """Similarity scores."""
    
    sources: List[str]
    """Document sources (manuals, papers, summaries)."""


# =============================================================================
# CONTEXT BUILDER MODELS
# =============================================================================

class LLMContext(BaseModel):
    """Context prepared for response generation."""
    
    metadata: Optional[MetadataResult] = None
    statistics: Optional[StatisticsResult] = None
    spatial: Optional[SpatialResult] = None
    cde: Optional[CDEResult] = None
    embeddings: Optional[List[EmbeddingResult]] = None
    
    query_summary: str
    """Natural language summary of what was found."""
    
    data_quality: Literal["high", "medium", "low"] = "high"
    """Confidence in the data quality."""


# =============================================================================
# RESPONSE GENERATOR MODELS
# =============================================================================

class SourceReference(BaseModel):
    """Reference to data source."""
    
    type: Literal["metadata", "cde", "qdrant", "statistics"]
    """Source type."""
    
    id: Optional[str] = None
    """Source identifier."""
    
    description: str
    """Human-readable description."""


class ResponseGeneration(BaseModel):
    """Final response to user."""
    
    answer: str
    """Natural language answer."""
    
    sources: List[SourceReference]
    """Sources used for the answer."""
    
    simulations: Optional[List[Dict[str, Any]]] = None
    """Detailed simulation data if requested."""
    
    confidence: Literal["high", "medium", "low"]
    """Confidence in the answer."""
    
    limitations: Optional[List[str]] = None
    """Known limitations or caveats."""


# =============================================================================
# AGENTIC PLANNER V2 (Structured Outputs)
# =============================================================================

ToolName = Literal["query_simulation_data", "query_cde", "semantic_search"]


class SimulationSpatialInput(BaseModel):
    type: Optional[Literal["radius", "polygon", "country", "state", "district", "bounding_box", "nearest"]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: Optional[int] = None
    polygon_wkt: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    bounding_box: Optional[Dict[str, float]] = None


class SimulationToolInput(BaseModel):
    filters: Dict[str, Any] = Field(default_factory=dict)
    metrics: List[str] = Field(default_factory=list)
    aggregation: Optional[Literal["AVG", "MAX", "MIN", "COUNT", "SUM"]] = None
    group_by: List[str] = Field(default_factory=list)
    spatial: Optional[SimulationSpatialInput] = None


class SimulationStatistics(BaseModel):
    aggregation_type: Optional[str] = None
    metric: Optional[str] = None
    value: Optional[float] = None
    count: int = 0
    breakdown: Optional[Dict[str, Any]] = None
    unit: Optional[str] = None


class SimulationToolOutput(BaseModel):
    simulations: List[Dict[str, Any]] = Field(default_factory=list)
    statistics: Optional[SimulationStatistics] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CDEToolInput(BaseModel):
    variables: List[str] = Field(default_factory=list)
    cultivars: List[str] = Field(default_factory=list)


class CDEToolOutput(BaseModel):
    definitions: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, Any] = Field(default_factory=dict)


class SemanticToolInput(BaseModel):
    query: str
    top_k: int = 5


class SemanticToolOutput(BaseModel):
    documents: List[Dict[str, Any]] = Field(default_factory=list)


class PlannerToolCall(BaseModel):
    tool: ToolName
    parameters: Union[SimulationToolInput, CDEToolInput, SemanticToolInput]


class PlannerOutput(BaseModel):
    goal: str
    tools: List[PlannerToolCall]


# =============================================================================
# ERROR MODELS
# =============================================================================

class ToolError(BaseModel):
    """Tool execution error."""
    
    tool_name: str
    """Name of the tool that failed."""
    
    error_type: str
    """Type of error."""
    
    message: str
    """Error message."""
    
    details: Optional[Dict[str, Any]] = None
    """Additional error details."""


class OrchestratorResponse(BaseModel):
    """Orchestrator response wrapper."""
    
    success: bool
    """Whether the orchestration succeeded."""
    
    query_plan: Optional[QueryPlan] = None
    """Generated query plan."""
    
    context: Optional[LLMContext] = None
    """Built context."""
    
    response: Optional[ResponseGeneration] = None
    """Final response."""
    
    errors: List[ToolError] = []
    """Any tool execution errors."""
    
    timing: Dict[str, float]
    """Timing information for each step."""
