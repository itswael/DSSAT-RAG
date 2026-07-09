# DSSAT RAG Backend

Production-grade Python backend for DSSAT simulation chatbot using FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL + PostGIS, and Qdrant.

## Features

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **PostgreSQL + PostGIS** - Spatial database with geometry support
- **Qdrant** - Vector database for embeddings (ready for future implementation)
- **Repository Pattern** - Clean separation of concerns
- **Service Layer** - Business logic separation
- **Pydantic Models** - Type validation and serialization

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   └── v1/          # Version 1 API routes
│   ├── core/            # Core configuration
│   ├── db/              # Database setup
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── repositories/    # Repository pattern implementation
│   ├── services/        # Service layer
│   ├── parsers/         # CSV and data parsers
│   ├── mappers/         # Data mapping utilities
│   └── utils/           # Utility functions
├── alembic/             # Database migrations
├── requirements.txt     # Python dependencies
└── main.py              # Application entry point
```

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ with PostGIS extension
- Qdrant (optional, for future embeddings)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
- `GET /health/status` - Health check endpoint
- `GET /` - Root endpoint

### Ingestion
- `POST /api/v1/ingest/` - Ingest a DSSAT summary CSV file
- `POST /api/v1/ingest/batch` - Ingest multiple CSV files

## Database Schema

### Simulations Table
- `simulation_id` (UUID, PK)
- `experiment_name`, `run_name`
- `country`, `state`, `district`
- `ecological_zone`
- `latitude`, `longitude`
- `location` (PostGIS Geometry(Point,4326))
- `geohash`
- `crop`, `cultivar`
- `irrigation`, `nitrogen_level`
- `planting_stage`, `planting_date`, `harvest_date`
- `simulation_year`
- `harvest_area`

### Simulation Outputs Table
- `id` (PK)
- `simulation_id` (FK to simulations)
- `variable_code`
- `value`
- `unit`

## Development

### Running Migrations

```bash
# Create new migration
alembic revision -m "migration message"

# Apply migrations
alembic upgrade head

# Downgrade migrations
alembic downgrade -1
```

### Code Structure

The application follows a clean architecture pattern:

- **Models**: Database schema definitions
- **Schemas**: Pydantic models for API validation
- **Repositories**: Data access layer
- **Services**: Business logic layer
- **API**: HTTP endpoints

## Future Enhancements

- Qdrant integration for vector embeddings
- LLM integration for chatbot functionality
- CDE (Crop Data Exchange) support
- Advanced spatial queries with PostGIS
- Real-time data processing
