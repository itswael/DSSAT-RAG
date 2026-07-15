"""Query Planner - converts natural language to QueryPlan."""
import json
import logging
from typing import Optional

from openai import AsyncOpenAI
from pydantic import ValidationError

from app.agent.models import QueryPlan
from app.agent.prompts import get_planner_prompt
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Get settings instance
settings = get_settings()


class QueryPlanner:
    """Plans query execution using LLM."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize planner.
        
        Args:
            api_key: OpenAI API key (optional, uses env var if not provided)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
    
    async def plan(self, user_query: str) -> QueryPlan:
        """
        Plan query execution.
        
        Args:
            user_query: Natural language user query
            
        Returns:
            QueryPlan with execution instructions
        """
        logger.info(f"Planning query: {user_query}")

        # If no API key, skip LLM and use fallback
        if not self.client:
            return self._fallback_plan(user_query)

        prompt = get_planner_prompt(user_query)

        try:
            response = await self.client.responses.create(
                model="gpt-4o",
                temperature=0.1,
                max_tokens=2000,
                tools=[
                    {
                        "type": "function",
                        "name": "query_plan",
                        "description": "Generate a query execution plan from natural language",
                        "parameters": QueryPlan.model_json_schema()
                    }
                ],
                tool_choice={
                    "type": "function",
                    "function": {"name": "query_plan"}
                },
                input=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract the function call response
            for output in response.output:
                if output.type == "function_call":
                    plan_data = json.loads(output.arguments)
                    query_plan = QueryPlan(**plan_data)
                    logger.info(f"Generated query plan: {query_plan.intent}")
                    return query_plan
            
            raise ValueError("No query plan generated")
            
        except ValidationError as e:
            logger.error(f"Query plan validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            raise
    
    async def plan_with_fallback(self, user_query: str) -> QueryPlan:
        """
        Plan query with fallback to simpler parsing.
        
        Args:
            user_query: Natural language user query
            
        Returns:
            QueryPlan or default plan if LLM fails
        """
        # If LLM is unavailable, go straight to fallback
        if not self.client:
            return self._fallback_plan(user_query)

        try:
            return await self.plan(user_query)
        except Exception as e:
            logger.warning(f"LLM planning failed, using fallback: {e}")
            return self._fallback_plan(user_query)
    
    def _fallback_plan(self, user_query: str) -> QueryPlan:
        """
        Create fallback plan when LLM fails.
        
        Args:
            user_query: Natural language query
            
        Returns:
            Default QueryPlan
        """
        # Simple keyword-based parsing for fallback
        query_lower = user_query.lower()
        
        intent = "metadata"
        required_tools = ["metadata"]
        
        if any(word in query_lower for word in ["average", "mean", "total", "sum"]):
            intent = "aggregate"
            required_tools.append("statistics")
        elif any(word in query_lower for word in ["within", "near", "radius", "distance"]):
            intent = "spatial_search"
            required_tools.append("spatial")
        elif any(word in query_lower for word in ["compare", "vs", "versus"]):
            intent = "comparison"
            required_tools.append("statistics")
        
        return QueryPlan(
            intent=intent,
            filters={},
            required_tools=required_tools,
            response_type="summary"
        )
