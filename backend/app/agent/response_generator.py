"""Response Generator - generates final answers using LLM."""
import logging
from typing import Optional

from openai import AsyncOpenAI

from app.agent.models import ResponseGeneration, SourceReference
from app.agent.prompts import get_response_prompt, SYSTEM_PROMPT
from app.core.config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generates final responses using LLM."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize response generator.
        
        Args:
            api_key: OpenAI API key (optional)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        if self.api_key:
            if settings.OPENAI_BASE_URL:
                self.client = AsyncOpenAI(api_key=self.api_key, base_url=settings.OPENAI_BASE_URL)
            else:
                self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    async def generate(
        self,
        user_question: str,
        context: "LLMContext",
        query_plan: Optional["QueryPlan"] = None
    ) -> ResponseGeneration:
        """
        Generate response from context.
        
        Args:
            user_question: Original user question
            context: Built LLMContext
            query_plan: Query plan (optional)
            
        Returns:
            Generated response
        """
        logger.info("Generating response")
        logger.info(f"Response LLM configured: key={'set' if bool(self.api_key) else 'missing'}, model={settings.OPENAI_MODEL}")

        # If no LLM, build a simple heuristic answer from context
        if not self.client:
            answer = self._heuristic_answer(context, user_question)
            sources = self._build_sources(context)
            confidence = self._assess_confidence(context, answer)
            return ResponseGeneration(
                answer=answer,
                sources=sources,
                confidence=confidence,
                limitations=self._identify_limitations(context)
            )

        # Format context and get prompt
        context_str = self._format_context(context)
        prompt = get_response_prompt(context, user_question)

        try:
            # Use Chat Completions
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL or "gpt-oss-120b",
                temperature=0.3,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )

            answer = response.choices[0].message.content or ""

            sources = self._build_sources(context)
            confidence = self._assess_confidence(context, answer)

            return ResponseGeneration(
                answer=answer,
                sources=sources,
                confidence=confidence,
                limitations=self._identify_limitations(context)
            )

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return ResponseGeneration(
                answer="I encountered an error generating the response. Please try again.",
                sources=[],
                confidence="low",
                limitations=["LLM service unavailable"]
            )

    def _heuristic_answer(self, context: "LLMContext", user_question: str) -> str:
        """Produce a simple answer without LLM based on available context."""
        parts = []
        if context.statistics and context.statistics.value is not None:
            parts.append(
                f"{context.statistics.aggregation_type.title()} {context.statistics.metric}: {context.statistics.value:.2f}"
            )
        if context.metadata and context.metadata.total_count:
            parts.append(f"Found {context.metadata.total_count} matching simulations")
        return ". ".join(parts) if parts else "Query executed successfully"
    
    def _format_context(self, context: "LLMContext") -> str:
        """Format context for prompt."""
        parts = []
        
        # Query summary
        if context.query_summary:
            parts.append(f"Query Summary: {context.query_summary}")
        
        # Metadata
        if context.metadata and context.metadata.simulations:
            sim_count = len(context.metadata.simulations)
            parts.append(f"\nFound {sim_count} matching simulation(s)")
            
            # Add sample
            for sim in context.metadata.simulations[:3]:
                parts.append(f"- {sim.get('experiment_name', 'Unknown')}: "
                          f"{sim.get('crop', '')} in {sim.get('country', '')}")
        
        # Statistics
        if context.statistics and context.statistics.value is not None:
            parts.append(f"\n{context.statistics.aggregation_type.title()} value: "
                        f"{context.statistics.value:.2f} (count: {context.statistics.count})")
        
        # CDE
        if context.cde and context.cde.variable_definitions:
            parts.append("\nVariable definitions:")
            for var in context.cde.variable_definitions[:3]:
                parts.append(f"- {var.get('full_name', 'Unknown')}: {var.get('description', '')}")
        
        # Embeddings
        if context.embeddings:
            doc_count = sum(len(e.documents) for e in context.embeddings)
            parts.append(f"\nFound {doc_count} relevant document(s)")
        
        return "\n".join(parts)
    
    def _build_sources(self, context: "LLMContext") -> list:
        """Build source references."""
        sources = []
        
        if context.metadata and context.metadata.total_count > 0:
            sources.append(SourceReference(
                type="metadata",
                description=f"Database: {context.metadata.total_count} simulation records"
            ))
        
        if context.statistics and context.statistics.count > 0:
            sources.append(SourceReference(
                type="statistics",
                description=f"Aggregated statistics from {context.statistics.count} records"
            ))
        
        if context.cde and context.cde.variable_definitions:
            sources.append(SourceReference(
                type="cde",
                description="Crop Data Exchange definitions"
            ))
        
        if context.embeddings:
            for emb in context.embeddings:
                if emb.documents:
                    sources.append(SourceReference(
                        type="qdrant",
                        description=f"Document search: {emb.sources[0] if emb.sources else 'unknown'}"
                    ))
                    break  # Only add once
        
        return sources
    
    def _assess_confidence(self, context: "LLMContext", answer: str) -> str:
        """Assess confidence in the answer."""
        # Check for uncertainty phrases
        uncertainty_phrases = [
            "I cannot",
            "I don't have enough information",
            "Data not available",
            "Unable to determine"
        ]
        
        if any(phrase.lower() in answer.lower() for phrase in uncertainty_phrases):
            return "low"
        
        # Check data quality
        if context.data_quality == "high":
            return "high"
        elif context.data_quality == "medium":
            return "medium"
        else:
            return "low"
    
    def _identify_limitations(self, context: "LLMContext") -> list:
        """Identify limitations in the response."""
        limitations = []
        
        # Check for low data quality
        if context.data_quality == "low":
            limitations.append("Limited data available")
        
        # Check for missing filters
        if not context.metadata and not context.spatial:
            limitations.append("No matching simulations found")
        
        return limitations
