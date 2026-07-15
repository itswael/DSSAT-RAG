"""Query Planner - converts natural language to QueryPlan."""
import json
import logging
import re
from typing import Optional, Any, Dict

from openai import AsyncOpenAI
from pydantic import ValidationError

from app.agent.models import QueryPlan
from app.agent.prompts import get_planner_prompt
from app.core.config import get_settings
from app.services.statistics_service import StatisticsService

logger = logging.getLogger(__name__)

# Get settings instance
settings = get_settings()


class QueryPlanner:
    """Plans query execution using LLM."""

    def __init__(self, api_key: Optional[str] = None, db_session=None):
        """Initialize planner with optional LLM and DB access."""
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.db_session = db_session
        if self.api_key:
            if settings.OPENAI_BASE_URL:
                self.client = AsyncOpenAI(api_key=self.api_key, base_url=settings.OPENAI_BASE_URL)
            else:
                self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None

    async def plan(self, user_query: str) -> QueryPlan:
        """Plan query execution using LLM tool-calling."""
        logger.info(f"Planning query: {user_query}")
        logger.info(f"Planner LLM configured: key={'set' if bool(self.api_key) else 'missing'}, model={settings.OPENAI_MODEL}")

        if not self.client:
            return await self._fallback_plan(user_query)

        prompt = get_planner_prompt(user_query)

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL or "gpt-oss-120b",
                temperature=0.1,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "query_plan",
                            "description": "Generate a query execution plan from natural language",
                            "parameters": QueryPlan.model_json_schema(),
                        },
                    }
                ],
                tool_choice={
                    "type": "function",
                    "function": {"name": "query_plan"},
                },
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

            choice = response.choices[0]
            tool_calls = getattr(choice.message, "tool_calls", None) or []
            logger.info(f"Planner tool_calls count: {len(tool_calls)}")
            for call in tool_calls:
                if call.type == "function" and call.function and call.function.name == "query_plan":
                    raw_args = call.function.arguments or "{}"
                    logger.info(f"Planner raw tool args: {raw_args}")
                    try:
                        plan_data = json.loads(raw_args)
                    except Exception:
                        try:
                            plan_data = json.loads(json.loads(raw_args))
                        except Exception:
                            logger.warning("Planner returned non-JSON tool arguments; falling back")
                            raise ValueError("Invalid tool arguments")
                    # Coerce common LLM schema drift into expected shape
                    try:
                        if not isinstance(plan_data, dict):
                            plan_data = {}
                        # Accept alternate key names
                        if "filter" in plan_data and "filters" not in plan_data:
                            plan_data["filters"] = plan_data.pop("filter") if isinstance(plan_data.get("filter"), dict) else {}
                        # Accept other variants for tools
                        if "tools" in plan_data and "required_tools" not in plan_data:
                            plan_data["required_tools"] = plan_data.pop("tools")
                        if "tool" in plan_data and "required_tools" not in plan_data:
                            plan_data["required_tools"] = [plan_data.pop("tool")]
                        if "requiredTools" in plan_data and "required_tools" not in plan_data:
                            rt = plan_data.pop("requiredTools")
                            plan_data["required_tools"] = rt if isinstance(rt, list) else ["metadata"]
                        # Normalize aggregation to uppercase literal
                        if plan_data.get("aggregation"):
                            plan_data["aggregation"] = str(plan_data["aggregation"]).upper()
                            if plan_data["aggregation"] in {"AVERAGE", "MEAN"}:
                                plan_data["aggregation"] = "AVG"
                        # Normalize intent if it's an unexpected value
                        allowed_intents = {"metadata", "aggregate", "spatial_search", "comparison", "trend", "explanation", "hybrid"}
                        intent = plan_data.get("intent")
                        ql = user_query.lower()
                        if not intent or intent not in allowed_intents:
                            if any(w in ql for w in ["average", "avg", "mean", "total", "sum"]) or plan_data.get("aggregation") or plan_data.get("metric"):
                                plan_data["intent"] = "aggregate"
                            else:
                                plan_data["intent"] = "metadata"
                        # Ensure filters exists and move stray top-level filters into it
                        if not isinstance(plan_data.get("filters"), dict):
                            plan_data["filters"] = {}
                        flt = plan_data["filters"]
                        for key in ["crop", "cultivar", "year", "state", "district", "country"]:
                            if key in plan_data and key not in flt:
                                flt[key] = plan_data.pop(key)
                        plan_data["filters"] = flt
                        # Ensure required_tools contains needed tools
                        allowed_tools = {"metadata", "spatial", "statistics", "cde", "embedding"}
                        if not isinstance(plan_data.get("required_tools"), list):
                            plan_data["required_tools"] = ["metadata"]
                        # Filter out any non-allowed tools from the list
                        plan_data["required_tools"] = [t for t in plan_data["required_tools"] if isinstance(t, str) and t in allowed_tools]
                        if not plan_data["required_tools"]:
                            plan_data["required_tools"] = ["metadata"]
                        if plan_data.get("intent") == "aggregate" and "statistics" not in plan_data["required_tools"]:
                            plan_data["required_tools"].append("statistics")
                        # Validate response_type, default to summary on bad values
                        if plan_data.get("response_type") not in {"summary", "detailed", "comparison", "trend"}:
                            plan_data["response_type"] = "summary"
                        # Drop any unknown top-level keys to avoid validation errors
                        allowed = set(QueryPlan.model_fields.keys())
                        plan_data = {k: v for k, v in plan_data.items() if k in allowed}
                    except Exception as coerce_err:
                        logger.warning(f"Planner schema coercion failed: {coerce_err}")
                    query_plan = QueryPlan(**plan_data)
                    logger.info(f"Generated query plan: intent={query_plan.intent}, metric={query_plan.metric}, aggregation={query_plan.aggregation}, filters={query_plan.filters}")
                    return query_plan

            # If no valid tool call, try parsing JSON directly from content
            raw_content = getattr(choice.message, "content", None)
            if raw_content:
                logger.info(f"Planner raw message content: {raw_content[:400]}")
                content_text = raw_content if isinstance(raw_content, str) else str(raw_content)
                # Try direct JSON parse
                plan_data = None
                try:
                    plan_data = json.loads(content_text)
                except Exception:
                    # Extract first JSON object substring and parse
                    try:
                        m = re.search(r"\{[\s\S]*\}", content_text)
                        if m:
                            plan_data = json.loads(m.group(0))
                    except Exception:
                        plan_data = None
                if plan_data is not None:
                    try:
                        if not isinstance(plan_data, dict):
                            plan_data = {}
                        if "filter" in plan_data and "filters" not in plan_data:
                            plan_data["filters"] = plan_data.pop("filter") if isinstance(plan_data.get("filter"), dict) else {}
                        if "tools" in plan_data and "required_tools" not in plan_data:
                            plan_data["required_tools"] = plan_data.pop("tools")
                        if "tool" in plan_data and "required_tools" not in plan_data:
                            plan_data["required_tools"] = [plan_data.pop("tool")]
                        if plan_data.get("aggregation"):
                            plan_data["aggregation"] = str(plan_data["aggregation"]).upper()
                            if plan_data["aggregation"] in {"AVERAGE", "MEAN"}:
                                plan_data["aggregation"] = "AVG"
                        allowed_intents = {"metadata", "aggregate", "spatial_search", "comparison", "trend", "explanation", "hybrid"}
                        intent = plan_data.get("intent")
                        if not intent or intent not in allowed_intents:
                            ql = user_query.lower()
                            if any(w in ql for w in ["average", "avg", "mean", "total", "sum"]) or plan_data.get("aggregation") or plan_data.get("metric"):
                                plan_data["intent"] = "aggregate"
                            else:
                                plan_data["intent"] = "metadata"
                        if not isinstance(plan_data.get("filters"), dict):
                            plan_data["filters"] = {}
                        flt = plan_data["filters"]
                        for key in ["crop", "cultivar", "year", "state", "district", "country"]:
                            if key in plan_data and key not in flt:
                                flt[key] = plan_data.pop(key)
                        plan_data["filters"] = flt
                        allowed_tools = {"metadata", "spatial", "statistics", "cde", "embedding"}
                        if not isinstance(plan_data.get("required_tools"), list):
                            plan_data["required_tools"] = ["metadata"]
                        plan_data["required_tools"] = [t for t in plan_data["required_tools"] if isinstance(t, str) and t in allowed_tools]
                        if not plan_data["required_tools"]:
                            plan_data["required_tools"] = ["metadata"]
                        if plan_data.get("intent") == "aggregate" and "statistics" not in plan_data["required_tools"]:
                            plan_data["required_tools"].append("statistics")
                        if plan_data.get("response_type") not in {"summary", "detailed", "comparison", "trend"}:
                            plan_data["response_type"] = "summary"
                        allowed = set(QueryPlan.model_fields.keys())
                        plan_data = {k: v for k, v in plan_data.items() if k in allowed}
                    except Exception as coerce_err:
                        logger.warning(f"Planner content schema coercion failed: {coerce_err}")
                    query_plan = QueryPlan(**plan_data)
                    logger.info(f"Generated query plan (content): intent={query_plan.intent}, metric={query_plan.metric}, aggregation={query_plan.aggregation}, filters={query_plan.filters}")
                    return query_plan

            raise ValueError("No query plan generated via tool call or content")

        except ValidationError as e:
            logger.error(f"Query plan validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            raise

    async def plan_with_fallback(self, user_query: str) -> QueryPlan:
        """Plan query with fallback to simpler parsing and DB-driven enrichment."""
        if not self.client:
            return await self._fallback_plan(user_query)

        try:
            qp = await self.plan(user_query)
            # Enrich if aggregate intent implied but fields missing
            ql = user_query.lower()
            if (not qp.metric or not qp.aggregation) and any(w in ql for w in ["average", "avg", "mean", "total", "sum"]):
                logger.info("Planner: enriching aggregate plan (missing metric/aggregation)")
                qp.aggregation = qp.aggregation or "AVG"
                stats = None
                if self.db_session is not None:
                    try:
                        if hasattr(self.db_session, 'session'):
                            db = await self.db_session.session()
                        else:
                            db = self.db_session
                        stats = StatisticsService(db)
                    except Exception:
                        stats = None
                if stats and not qp.metric:
                    try:
                        qp.metric = await stats.resolve_metric_from_text(user_query)
                        logger.info(f"Planner: resolved metric via DB -> {qp.metric}")
                    except Exception:
                        pass
                # Secondary heuristic: capture explicit uppercase codes in the query (e.g., HWAM)
                if not qp.metric:
                    mcode = re.search(r"\b[A-Z]{3,6}\b", user_query)
                    if mcode:
                        qp.metric = mcode.group(0)
                        logger.info(f"Planner: resolved metric via uppercase heuristic -> {qp.metric}")
                if "year" not in qp.filters:
                    m = re.search(r"\b(19|20)\d{2}\b", ql)
                    if m:
                        try:
                            qp.filters["year"] = int(m.group(0))
                        except Exception:
                            pass
                if stats and "crop" not in qp.filters:
                    try:
                        crop_resolved = await stats.resolve_crop_from_text(user_query)
                        if crop_resolved:
                            qp.filters["crop"] = crop_resolved
                            logger.info(f"Planner: resolved crop via DB -> {crop_resolved}")
                    except Exception:
                        pass
                if "statistics" not in qp.required_tools:
                    qp.required_tools.append("statistics")
                if qp.intent != "aggregate":
                    qp.intent = "aggregate"
            return qp
        except Exception as e:
            logger.warning(f"LLM planning failed, using fallback: {e}")
            return await self._fallback_plan(user_query)

    async def _fallback_plan(self, user_query: str) -> QueryPlan:
        """Create fallback plan using data-driven resolution only (no hardcoded maps)."""
        query_lower = user_query.lower()

        intent = "metadata"
        required_tools = ["metadata"]
        filters: Dict[str, Any] = {}

        if any(word in query_lower for word in ["average", "avg", "mean", "total", "sum"]):
            intent = "aggregate"
            required_tools.append("statistics")
            # Resolve metric/crop dynamically using DB if available
            stats = None
            if self.db_session is not None:
                try:
                    if hasattr(self.db_session, 'session'):
                        db = await self.db_session.session()
                    else:
                        db = self.db_session
                    stats = StatisticsService(db)
                except Exception:
                    stats = None
            metric_resolved = None
            if stats:
                try:
                    metric_resolved = await stats.resolve_metric_from_text(user_query)
                except Exception:
                    metric_resolved = None
            # Secondary heuristic: capture explicit uppercase codes in the query (e.g., HWAM)
            if not metric_resolved:
                mcode = re.search(r"\b[A-Z]{3,6}\b", user_query)
                if mcode:
                    metric_resolved = mcode.group(0)
            # Extract year
            m = re.search(r"\b(19|20)\d{2}\b", query_lower)
            if m:
                try:
                    filters["year"] = int(m.group(0))
                except Exception:
                    pass
            # Extract crop dynamically
            crop_resolved = None
            if stats:
                try:
                    crop_resolved = await stats.resolve_crop_from_text(user_query)
                except Exception:
                    crop_resolved = None
            if crop_resolved:
                filters["crop"] = crop_resolved
            # Only produce an aggregate plan when a metric is resolved
            if metric_resolved:
                return QueryPlan(
                    intent=intent,
                    filters=filters,
                    required_tools=required_tools,
                    response_type="summary",
                    metric=metric_resolved,
                    aggregation="AVG",
                )
        elif any(word in query_lower for word in ["within", "near", "radius", "distance"]):
            intent = "spatial_search"
            required_tools.append("spatial")
        elif any(word in query_lower for word in ["compare", "vs", "versus"]):
            intent = "comparison"
            required_tools.append("statistics")

        # Extract simple filters
        m = re.search(r"\b(19|20)\d{2}\b", query_lower)
        if m:
            try:
                filters["year"] = int(m.group(0))
            except Exception:
                pass
        if self.db_session is not None:
            try:
                if hasattr(self.db_session, 'session'):
                    db = await self.db_session.session()
                else:
                    db = self.db_session
                stats = StatisticsService(db)
                crop_resolved = await stats.resolve_crop_from_text(user_query)
                if crop_resolved:
                    filters["crop"] = crop_resolved
            except Exception:
                pass

        return QueryPlan(
            intent=intent,
            filters=filters,
            required_tools=required_tools,
            response_type="summary",
        )
