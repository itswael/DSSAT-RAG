# Agent Orchestrator

Production-grade AI Agent Orchestrator for DSSAT RAG platform.

## Architecture

```
User Query
    ↓
Query Planner (LLM)
    ↓
Execution Planner
    ↓
Parallel Tool Calls
├── Metadata Tool
├── Spatial Tool  
├── Statistics Tool
├── CDE Tool
└── Embedding Tool
    ↓
Context Builder
    ↓
Response Generator (LLM)
    ↓
Structured Response
```

## Components

### 1. Query Planner (`agent/planner.py`)
- Converts natural language to structured `QueryPlan`
- Uses OpenAI Responses API with tool calling
- Never writes SQL - only generates execution instructions

### 2. Tools (`app/services/`)

#### Metadata Service
- Get simulation records by filters
- Retrieve simulation outputs
- Get unique values (crops, cultivars, years)
- Crop summary statistics

#### Spatial Service  
- Radius search (ST_DWithin approximation)
- Polygon search (ST_Within)
- Region-based search (country, state, district, ecological zone)
- Bounding box calculations

#### Statistics Service
- Aggregate calculations (AVG, MIN, MAX, COUNT, SUM)
- Breakdown by category (cultivar, year, etc.)
- Variable statistics (min, max, avg, stddev)
- Yearly trend analysis
- Top simulations ranking

#### CDE Service
- Variable definitions and descriptions
- Variable relationships
- Cultivar information
- Species information
- Synonym lookup

#### Embedding Service
- Semantic search using Qdrant
- Search manuals, papers, summaries
- Filter by crop, year, location

### 3. Executor (`agent/executor.py`)
- Executes tools in parallel using `asyncio.gather()`
- Handles errors gracefully
- Collects results from all tools
- Builds timing information

### 4. Context Builder (`agent/context_builder.py`)
- Merges tool outputs into unified context
- Removes duplicates
- Adds metadata about data quality
- Generates natural language summary

### 5. Response Generator (`agent/response_generator.py`)
- Uses OpenAI Responses API for final answer
- Formats context for LLM consumption
- Builds source references
- Assesses confidence level

### 6. Orchestrator (`agent/orchestrator.py`)
- Main coordinator for the agent workflow
- Handles errors comprehensively
- Returns structured response with timing

## Usage

```python
from app.agent.orchestrator import AgentOrchestrator

# Create orchestrator
orchestrator = AgentOrchestrator(db_session=db)

# Execute query
response = await orchestrator.orchestrate_with_error_handling(
    "Average maize yield within 50 km of Gainesville in 2022"
)

print(response.response.answer)
print(response.context.statistics.value)
```

## Query Types Supported

1. **Metadata**: "Show simulations for maize"
2. **Aggregate**: "Average HWAM in Florida"
3. **Spatial**: "Within 25 km of Gainesville"
4. **Comparison**: "Compare cultivars A and B"
5. **Trend**: "Yield trend over time"
6. **Explanation**: "Why was yield low?"
7. **Hybrid**: Combine multiple intents

## Configuration

```python
# Environment variables
OPENAI_API_KEY=your_api_key_here
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Output Format

```json
{
    "answer": "Natural language answer",
    "sources": [
        {"type": "metadata", "description": "..."},
        {"type": "statistics", "description": "..."}
    ],
    "simulations": [...],
    "confidence": "high|medium|low",
    "query_plan": {...},
    "timing": {
        "planning": 0.5,
        "execution": 1.2,
        "generation": 0.8,
        "total": 2.5
    }
}
```

## Error Handling

- Partial failures: Continue with available data
- Tool errors: Logged and reported in response
- Fallback plans: Simple keyword-based parsing if LLM fails
- Always succeeds: Returns structured error information
