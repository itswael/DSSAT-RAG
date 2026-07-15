"""Example usage of Agent Orchestrator."""
import asyncio

from app.agent.orchestrator import AgentOrchestrator


async def example_basic_query():
    """Basic query example."""
    # Create orchestrator (in production, inject db_session)
    orchestrator = AgentOrchestrator()
    
    # Execute query
    response = await orchestrator.orchestrate_with_error_handling(
        "Average maize yield within 50 km of Gainesville in 2022"
    )
    
    print("Answer:", response.response.answer if response.response else "")
    print("Confidence:", response.response.confidence if response.response else "")


async def example_spatial_query():
    """Spatial query example."""
    orchestrator = AgentOrchestrator()
    
    response = await orchestrator.orchestrate_with_error_handling(
        "Show all simulations for wheat in Florida"
    )
    
    print("Simulations:", len(response.context.metadata.simulations) if response.context and response.context.metadata else 0)


async def example_comparison_query():
    """Comparison query example."""
    orchestrator = AgentOrchestrator()
    
    response = await orchestrator.orchestrate_with_error_handling(
        "Compare HWAM between cultivar A and B in 2021"
    )
    
    print("Answer:", response.response.answer if response.response else "")


async def example_trend_query():
    """Trend query example."""
    orchestrator = AgentOrchestrator()
    
    response = await orchestrator.orchestrate_with_error_handling(
        "Show yield trend from 2010 to 2023"
    )
    
    print("Answer:", response.response.answer if response.response else "")


async def example_explanation_query():
    """Explanation query example."""
    orchestrator = AgentOrchestrator()
    
    response = await orchestrator.orchestrate_with_error_handling(
        "Why was yield low in Florida last year?"
    )
    
    print("Answer:", response.response.answer if response.response else "")
    print("Limitations:", response.response.limitations if response.response else [])


async def example_full_workflow():
    """Full workflow with all components."""
    orchestrator = AgentOrchestrator()
    
    # Step 1: Plan
    query_plan = await orchestrator.planner.plan_with_fallback(
        "Average HWAM for maize in Texas during 2021"
    )
    
    print("Query Plan:", query_plan.model_dump())
    
    # Step 2: Execute
    context = await orchestrator.executor.execute(query_plan)
    
    print("Context built:")
    print(f"  - Metadata: {context.metadata.total_count if context.metadata else 0} simulations")
    print(f"  - Statistics: {context.statistics.value if context.statistics else 'N/A'}")
    
    # Step 3: Generate response
    response = await orchestrator.response_generator.generate(
        user_question="Average HWAM for maize in Texas during 2021",
        context=context,
        query_plan=query_plan
    )
    
    print("Response:", response.answer)
    print("Sources:", [s.description for s in response.sources])


async def main():
    """Run all examples."""
    print("=" * 60)
    print("Agent Orchestrator Examples")
    print("=" * 60)
    
    # Run examples
    await example_basic_query()
    print("\n" + "=" * 60 + "\n")
    
    await example_spatial_query()
    print("\n" + "=" * 60 + "\n")
    
    await example_comparison_query()
    print("\n" + "=" * 60 + "\n")
    
    await example_trend_query()
    print("\n" + "=" * 60 + "\n")
    
    await example_explanation_query()
    print("\n" + "=" * 60 + "\n")
    
    await example_full_workflow()


if __name__ == "__main__":
    asyncio.run(main())
