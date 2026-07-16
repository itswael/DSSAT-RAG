"""Orchestrator - main agent coordinator.

Flow:
User → Planner (Structured Outputs) → Executor (parallel tools) → Context → Response Generator
"""
import logging
from typing import Optional

from datetime import datetime

from app.agent.models import (
    QueryPlan,
    LLMContext,
    ResponseGeneration,
    OrchestratorResponse
)
from app.agent.planner import QueryPlanner
from app.agent.executor import Executor
from app.agent.context_builder import ContextBuilder
from app.agent.response_generator import ResponseGenerator
from app.agent.models import PlannerOutput

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Main orchestrator for the agent system."""
    
    def __init__(
        self,
        db_session=None,
        planner_api_key: Optional[str] = None,
        response_api_key: Optional[str] = None
    ):
        """
        Initialize orchestrator.
        
        Args:
            db_session: Database session
            planner_api_key: OpenAI API key for planning (optional)
            response_api_key: OpenAI API key for response generation (optional)
        """
        self.db_session = db_session
        self.planner = QueryPlanner(api_key=planner_api_key, db_session=db_session)
        self.executor = Executor(db_session=db_session)
        self.context_builder = ContextBuilder()
        self.response_generator = ResponseGenerator(api_key=response_api_key)
    
    async def orchestrate(
        self,
        user_query: str
    ) -> OrchestratorResponse:
        """
        Orchestrate the full agent workflow.
        
        Args:
            user_query: Natural language user query
            
        Returns:
            Orchestrator response with all components
        """
        start_time = datetime.now()
        timing = {}
        errors = []
        
        try:
            # Step 1: Plan the query
            logger.info("Step 1: Planning query")
            plan_start = datetime.now()
            query_plan = await self.planner.plan_with_fallback(user_query)
            timing["planning"] = (datetime.now() - plan_start).total_seconds()
            planner_output: PlannerOutput | None = self.planner.get_last_planner_output()
            
            # Step 2: Execute tools
            logger.info(f"Step 2: Executing tools - {query_plan.required_tools}")
            exec_start = datetime.now()
            context = await self.executor.execute(query_plan, planner_output=planner_output)
            timing["execution"] = (datetime.now() - exec_start).total_seconds()
            
            # Step 3: Generate response
            logger.info("Step 3: Generating response")
            gen_start = datetime.now()
            response = await self.response_generator.generate(
                user_question=user_query,
                context=context,
                query_plan=query_plan
            )
            timing["generation"] = (datetime.now() - gen_start).total_seconds()
            
            # Calculate total time
            timing["total"] = (datetime.now() - start_time).total_seconds()
            
            return OrchestratorResponse(
                success=True,
                query_plan=query_plan,
                context=context,
                response=response,
                errors=errors,
                timing=timing
            )
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            
            # Calculate total time even on failure
            timing["total"] = (datetime.now() - start_time).total_seconds()
            
            return OrchestratorResponse(
                success=False,
                errors=[{
                    "tool_name": "orchestrator",
                    "error_type": type(e).__name__,
                    "message": str(e)
                }],
                timing=timing
            )
    
    async def orchestrate_with_error_handling(
        self,
        user_query: str
    ) -> OrchestratorResponse:
        """
        Orchestrate with comprehensive error handling.
        
        Args:
            user_query: Natural language user query
            
        Returns:
            Orchestrator response (always succeeds, even on partial failure)
        """
        start_time = datetime.now()
        timing = {}
        errors = []
        
        try:
            # Step 1: Plan
            logger.info("Step 1: Planning")
            plan_start = datetime.now()
            try:
                query_plan = await self.planner.plan_with_fallback(user_query)
            except Exception as e:
                logger.error(f"Planning failed: {e}")
                errors.append({
                    "tool_name": "planner",
                    "error_type": type(e).__name__,
                    "message": str(e)
                })
                # Create fallback plan
                query_plan = QueryPlan(
                    intent="metadata",
                    filters={},
                    required_tools=["metadata"],
                    response_type="summary"
                )
            timing["planning"] = (datetime.now() - plan_start).total_seconds()
            
            # Step 2: Execute
            logger.info("Step 2: Executing")
            exec_start = datetime.now()
            try:
                context = await self.executor.execute(query_plan)
            except Exception as e:
                logger.error(f"Execution failed: {e}")
                errors.append({
                    "tool_name": "executor",
                    "error_type": type(e).__name__,
                    "message": str(e)
                })
                # Create empty context
                from app.agent.models import LLMContext
                context = LLMContext(
                    query_summary="Partial execution completed",
                    data_quality="low"
                )
            timing["execution"] = (datetime.now() - exec_start).total_seconds()
            
            # Step 3: Generate response
            logger.info("Step 3: Generating response")
            gen_start = datetime.now()
            try:
                response = await self.response_generator.generate(
                    user_question=user_query,
                    context=context,
                    query_plan=query_plan
                )
            except Exception as e:
                logger.error(f"Response generation failed: {e}")
                errors.append({
                    "tool_name": "response_generator",
                    "error_type": type(e).__name__,
                    "message": str(e)
                })
                response = ResponseGeneration(
                    answer="I encountered an error processing your request. Please try again.",
                    sources=[],
                    confidence="low",
                    limitations=["Service unavailable"]
                )
            timing["generation"] = (datetime.now() - gen_start).total_seconds()
            
            # Total time
            timing["total"] = (datetime.now() - start_time).total_seconds()
            
            return OrchestratorResponse(
                success=True,
                query_plan=query_plan,
                context=context,
                response=response,
                errors=errors,
                timing=timing
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            timing["total"] = (datetime.now() - start_time).total_seconds()
            
            return OrchestratorResponse(
                success=False,
                errors=[{
                    "tool_name": "orchestrator",
                    "error_type": type(e).__name__,
                    "message": str(e)
                }],
                timing=timing
            )
