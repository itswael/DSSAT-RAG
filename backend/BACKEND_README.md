# DSSAT RAG Backend

Production-grade Python backend for DSSAT simulation chatbot.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   API    │  │ Services │  │ Repos    │  │  Models  │    │
│  │  Routes  │→ │  Layer   │→ │  Layer   │→ │  (ORM)   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                    ↓              ↓
            ┌──────────┐  ┌──────────┐
            │PostgreSQL│  │  Qdrant  │
            │ + PostGIS│  │ (Future) │
            └──────────┘  └──────────┘
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your configuration:

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Start the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use Docker:

```bash
docker-compose up -d
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Features

### SQLAlchemy Models with PostGIS

The `Simulation` model includes a PostGIS geometry field:

```python
location = Column(
    Geometry(geometry_type="POINT", srid=4326),
    nullable=False,
)
```

### Repository Pattern

Clean separation between data access and business logic:

```python
# In services/simulation.py
class SimulationService(BaseService[Simulation, SimulationCreate, dict]):
    def __init__(self, db: AsyncSession):
        self.repository = SimulationRepository(db)
```

### Service Layer

Business logic is separated from API endpoints:

```python
async def create_simulation(self, simulation_in: SimulationCreate) -> Simulation:
    simulation = map_simulation_create_to_model(simulation_in)
    return await self.repository.create(simulation)
```

## Database Schema

### Simulations Table

| Column | Type | Description |
|--------|------|-------------|
| simulation_id | UUID | Primary key |
| experiment_name | VARCHAR(255) | Experiment name |
| run_name | VARCHAR(255) | Run name |
| country | VARCHAR(100) | Country code |
| state | VARCHAR(100) | State/region |
| district | VARCHAR(100) | District |
| ecological_zone | VARCHAR(255) | Ecological zone |
| latitude | FLOAT | Latitude (WGS84) |
| longitude | FLOAT | Longitude (WGS84) |
| location | Geometry(Point,4326) | PostGIS geometry |
| geohash | VARCHAR(50) | Geohash representation |
| crop | VARCHAR(100) | Crop type |
| cultivar | VARCHAR(255) | Cultivar name |
| irrigation | VARCHAR(100) | Irrigation method |
| nitrogen_level | VARCHAR(100) | Nitrogen level |
| planting_stage | VARCHAR(100) | Planting stage |
| planting_date | DATE | Planting date |
| harvest_date | DATE | Harvest date |
| simulation_year | INT | Simulation year |
| harvest_area | FLOAT | Harvested area (ha) |

### Simulation Outputs Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| simulation_id | UUID | Foreign key to simulations |
| variable_code | VARCHAR(100) | Variable code |
| value | FLOAT | Variable value |
| unit | VARCHAR(50) | Unit of measurement |

## API Endpoints

### Health Check
- `GET /health/status` - Health check
- `GET /` - Root endpoint

### Ingestion
- `POST /api/v1/ingest/` - Ingest a CSV file
- `POST /api/v1/ingest/batch` - Ingest multiple CSV files

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

### Code Style

The project follows PEP 8 style guidelines with type hints.

## Future Enhancements

- Qdrant integration for vector embeddings
- LLM integration for chatbot functionality
- CDE (Crop Data Exchange) support
- Advanced spatial queries with PostGIS
- Real-time data processing
