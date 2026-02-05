# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Data Pipeline Validation System** - A data quality validation platform for monitoring data pipelines through automated testing. Currently in MVP phase with volume tests implemented.

**Key Documents**:
- **README_MVP.md** - Quick start guide
- **PRD.md** - Complete product requirements and planned test type specifications
- **ARCHITECTURE.md** - Technical architecture and database schemas
- **AGENTS.md** - Multi-agent framework specification (planned)

## Architecture

The system follows a **microservices-inspired architecture** with CQRS pattern:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  API Server │────▶│   Redis     │────▶│   Workers   │
│  (FastAPI)  │     │   Queue     │     │  (Celery)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                       │
       ▼                                       ▼
┌─────────────┐                      ┌─────────────┐
│  DynamoDB   │                      │ TimescaleDB │
│  (Config)   │                      │  (Results)  │
└─────────────┘                      └─────────────┘
```

**Dual Database Architecture**:
- **DynamoDB** stores test configurations, connections, users, audit logs
- **TimescaleDB** stores time-series test execution results

**Database Connectors**: SQL Server (pyodbc) and PostgreSQL (psycopg2-binary) are implemented. Add new connectors by implementing `BaseConnector` in `workers/connectors/base.py`.

## Common Commands

### Setup and Running

```bash
# Setup (AWS Development - uses AWS DynamoDB with local TimescaleDB/Redis)
./setup.sh  # or: cp .env.example .env && edit AWS_PROFILE

# Start services
docker-compose up -d                      # AWS hybrid mode
docker-compose -f docker-compose-local.yml up -d  # Fully local with DynamoDB Local

# Initialize DynamoDB Local tables (required for local mode only)
python scripts/init_dynamodb.py

# View logs
docker-compose logs -f
docker-compose logs -f api
docker-compose logs -f worker
```

### Running Without Docker

```bash
# API server
uvicorn api.main:app --reload --port 8000

# Celery worker
celery -A workers.celery_app worker --loglevel=info --concurrency=4
```

### Testing

```bash
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=api --cov=workers

# Run specific test file with verbose output
pytest tests/test_volume_executor.py -v

# Code quality
black . && flake8 . && mypy .
```

### API Usage (port 8001 externally)

```bash
# API docs
open http://localhost:8001/docs

# Create connection
curl -X POST http://localhost:8001/v1/connections -H "Content-Type: application/json" -d @examples/connection.json

# Create test
curl -X POST http://localhost:8001/v1/tests -H "Content-Type: application/json" -d @examples/volume_test.json

# Run test
curl -X POST http://localhost:8001/v1/tests/{test_id}/run

# View executions
curl http://localhost:8001/v1/executions?test_id={test_id}

# Dashboard summary
curl http://localhost:8001/v1/dashboard/summary
```

### Database Operations

```bash
# DynamoDB Local
aws dynamodb list-tables --endpoint-url http://localhost:8000
aws dynamodb scan --table-name Tests --endpoint-url http://localhost:8000

# TimescaleDB
docker exec -it dataquality-timescaledb psql -U dataquality -d dataquality_results
docker exec -it dataquality-timescaledb psql -U dataquality -d dataquality_results -c "SELECT * FROM test_executions ORDER BY started_at DESC LIMIT 5;"

# Redis
redis-cli -h localhost LLEN celery
```

### Terraform Deployment (AWS)

```bash
cd terraform
terraform init
cp terraform.tfvars.example terraform.tfvars  # Set rds_master_password
terraform plan
terraform apply
```

## Code Structure

```
api/
├── main.py              # FastAPI entry point
├── config.py            # Environment configuration (pydantic-settings)
├── routers/             # API endpoints (tests.py, executions.py, dashboard.py)
├── models/              # Pydantic models (test_config.py)
└── services/            # Business logic (dynamodb_client.py, timescaledb_client.py)

workers/
├── celery_app.py        # Celery configuration
├── executors/           # Test execution logic (volume_test.py)
├── connectors/          # Database connectors (base.py, sqlserver.py, postgres.py)
└── utils/               # Utilities (alert_sender.py)

scripts/
├── init_dynamodb.py     # Creates DynamoDB tables
└── init_timescaledb.sql # Creates TimescaleDB schema
```

## Key Implementation Patterns

### Test Execution Flow

1. `POST /v1/tests/{test_id}/run` triggers test
2. API publishes task to Redis via `workers.celery_app.execute_test_task`
3. Celery worker loads test config from DynamoDB
4. Worker creates connector and executes query (read-only)
5. Worker evaluates results against thresholds
6. Worker stores results in TimescaleDB `test_executions` table
7. Worker sends email alerts on failure via `workers/utils/alert_sender.py`

### Adding New Test Types

1. Create executor in `workers/executors/` following `volume_test.py` pattern
2. Create Celery task in `workers/tasks/`
3. Add Pydantic models in `api/models/test_config.py`
4. Reference PRD.md sections 3.1.2-3.1.6 for specifications

### Adding New Database Connectors

1. Create connector in `workers/connectors/` implementing `BaseConnector`
2. Register in `workers/connectors/__init__.py` `get_connector()`
3. Add driver to `requirements.txt`

## Configuration

### Port Mappings

- **API**: http://localhost:8001 (external), port 8000 internal
- **DynamoDB Local**: http://localhost:8000 (only with docker-compose-local.yml)
- **TimescaleDB**: localhost:5432
- **Redis**: localhost:6379

### AWS Authentication Modes (checked in order)

1. `DYNAMODB_ENDPOINT` - DynamoDB Local
2. `AWS_PROFILE` - AWS profile from ~/.aws/credentials
3. `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` - Explicit credentials
4. Default credentials - IAM role or environment

### Key Environment Variables

```bash
AWS_PROFILE=your_profile        # For AWS DynamoDB
DYNAMODB_ENDPOINT=http://localhost:8000  # For DynamoDB Local
RESULTS_DB_URL=postgresql://dataquality:password@localhost:5432/dataquality_results
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

## Troubleshooting

- **DynamoDB tables not found**: Run `python scripts/init_dynamodb.py` (local mode only)
- **Worker not processing**: Check `docker-compose logs -f worker` and `redis-cli -h localhost LLEN celery`
- **API errors**: Check `docker-compose logs -f api`
- **SQL Server**: Requires ODBC driver - macOS: `brew install unixodbc`

## What's Implemented vs Planned

**Implemented (MVP)**:
- Volume test executor
- SQL Server and PostgreSQL connectors
- FastAPI REST API
- DynamoDB + TimescaleDB storage
- Celery async execution
- Email alerts
- Terraform AWS deployment

**Planned** (see PRD.md):
- Distribution, Uniqueness, Referential, Pattern, Freshness tests
- Test scheduling (cron-based)
- Slack/PagerDuty integrations
- React dashboard
- Authentication/RBAC
