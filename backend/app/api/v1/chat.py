"""Chat endpoint for query execution."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.query import ChatRequest
from app.agent.orchestrator import AgentOrchestrator
from app.core.config import get_settings

router = APIRouter()


@router.post("/")
async def chat_query(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Execute a chat query using the agent orchestrator.

    Args:
        request: ChatRequest with user message
        db: Database session

    Returns:
        Query result
    """
    try:
        # Create orchestrator with database session (keys resolved internally)
        orchestrator = AgentOrchestrator(db_session=db)
        
        # Execute orchestration
        response = await orchestrator.orchestrate_with_error_handling(request.message)
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Orchestration failed: {response.errors}",
            )
        
        # Return structured response
        payload = {
            "answer": response.response.answer if response.response else "",
            "sources": [
                {"type": s.type, "description": s.description}
                for s in (response.response.sources if response.response else [])
            ],
            "simulations": (
                response.context.metadata.simulations 
                if response.context and response.context.metadata 
                else []
            ),
            "statistics": (
                response.context.statistics.model_dump()
                if response.context and response.context.statistics
                else None
            ),
            "confidence": response.response.confidence if response.response else "low",
            "query_plan": response.query_plan.model_dump() if response.query_plan else None,
            "timing": response.timing
        }
        return payload

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute query: {str(e)}",
        )


def _parse_message_to_plan(message: str):
    """
    Parse a natural language message into a QueryPlan.

    Args:
        message: User's natural language query

    Returns:
        QueryPlan with intent and filters
    """
    import re

    # Convert to lowercase for easier matching
    msg_lower = message.lower()

    # Determine intent based on keywords
    if any(word in msg_lower for word in ["average", "avg", "mean"]):
        intent = "aggregate"
        aggregation = "avg"
    elif any(word in msg_lower for word in ["maximum", "max", "highest"]):
        intent = "aggregate"
        aggregation = "max"
    elif any(word in msg_lower for word in ["minimum", "min", "lowest"]):
        intent = "aggregate"
        aggregation = "min"
    elif any(word in msg_lower for word in ["total", "sum"]):
        intent = "aggregate"
        aggregation = "sum"
    else:
        intent = "filter"
        aggregation = None

    # Extract metric (output variable)
    metric = None
    if any(word in msg_lower for word in ["yield", "harvest"]):
        metric = "HWAM"  # Harvest Weight of Moisture
    elif any(word in msg_lower for word in ["biomass", "weight"]):
        metric = "CWAM"
    elif any(word in msg_lower for word in ["precipitation", "rain", "prcp"]):
        metric = "PRCP"

    # Extract filters
    crop = None
    state = None
    year = None

    # Try to extract year (4 digits)
    year_match = re.search(r"\b(19|20)\d{2}\b", message)
    if year_match:
        year = int(year_match.group())

    # Extract country/state names (simplified)
    if "florida" in msg_lower or "fl" in msg_lower:
        state = "Florida"
    elif "california" in msg_lower or "ca" in msg_lower:
        state = "California"
    elif "texas" in msg_lower or "tx" in msg_lower:
        state = "Texas"

    # Extract crop type
    if "maize" in msg_lower or "corn" in msg_lower:
        crop = "Maize"
    elif "wheat" in msg_lower:
        crop = "Wheat"
    elif "rice" in msg_lower:
        crop = "Rice"

    return {
        "intent": intent,
        "metric": metric,
        "aggregation": aggregation,
        "filters": {
            "crop": crop,
            "state": state,
            "year": year,
        },
    }
