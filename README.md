# Pet Directory Service

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-94.79%25-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-009688)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/badge/linting-ruff-purple)](https://github.com/astral-sh/ruff)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue)](http://mypy-lang.org/)

A production-ready RESTful API service for managing a pet directory with real-time database change detection and automated reporting.

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Background Worker & Real-Time Change Detection](#background-worker--real-time-change-detection)
- [Database Access](#database-access)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [CI/CD Pipelines](#cicd-pipelines)
- [Design Choices and Reflection](#design-choices-and-reflection)

## Project Overview

This project implements a comprehensive pet directory system with enterprise-grade features:

- **FastAPI REST API**: Full CRUD operations with repository pattern for data access
- **PostgreSQL Database**: Persistent storage with async SQLAlchemy ORM 2.0+
- **Real-Time Change Detection**: PostgreSQL LISTEN/NOTIFY for instant database change reactions
- **Smart Background Worker**: Generates formatted reports on-demand when data changes
- **Comprehensive Testing**: 94.79% test coverage with pytest and async test support
- **Type Safety**: Full mypy type checking with strict mode enabled
- **Code Quality**: Automated linting with Ruff and Black formatting
- **CI/CD Ready**: GitHub Actions workflows for testing, building, and quality checks
- **Docker Containerization**: Multi-stage builds for production and development environments

## Key Features

### 🚀 Production-Ready Architecture
- **Async-First Design**: Full async/await implementation from database to API
- **Repository Pattern**: Clean separation of data access logic
- **Type-Safe**: Comprehensive type hints with mypy strict mode (zero type errors)
- **Pydantic V2**: Fast validation with Pydantic Settings for configuration
- **Health Checks**: Docker health checks ensure proper service orchestration

### 📊 Real-Time Change Detection
- **Event-Driven**: PostgreSQL LISTEN/NOTIFY for instant change notifications
- **Zero Polling**: Eliminates wasteful database queries
- **Sub-Second Latency**: Immediate report generation on data changes
- **Detailed Logging**: Tracks inserts, updates, deletes with full context

### 🧪 Comprehensive Testing
- **94.79% Coverage**: Extensive test suite covering all components
- **Async Test Support**: Full pytest-asyncio integration
- **Fixture-Based**: Reusable test fixtures for database and API testing
- **Mock Notifications**: Tests PostgreSQL LISTEN/NOTIFY without real database

### 🔒 Security & Quality
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency vulnerability checking
- **Ruff**: Modern, fast linting (replaces Flake8, isort, pyupgrade)
- **Black**: Consistent code formatting
- **Pre-commit Ready**: Hooks for automated quality checks

### 🐳 Docker & DevOps
- **Multi-Stage Builds**: Optimized production images (smaller, more secure)
- **Development Mode**: Hot-reload, Adminer UI, full dev tools
- **GitHub Actions**: Automated CI/CD with test, build, and quality pipelines
- **Layer Caching**: Fast builds with optimal Docker layer ordering

### 📝 Developer Experience
- **CLI Helper**: `dev.sh` script with intuitive commands
- **API Documentation**: Auto-generated Swagger and ReDoc interfaces
- **Type Hints**: Full IDE autocomplete and type checking
- **Clear Logging**: Structured logs with proper levels and formatting

### Project Structure

```
.
├── app/
│   ├── api/                      # REST API endpoints
│   │   └── pets.py               # Pet CRUD operations
│   ├── core/                     # Core configurations
│   │   ├── config.py             # Pydantic Settings configuration
│   │   ├── database.py           # Async database connection
│   │   └── dependencies.py       # FastAPI dependencies
│   ├── models/                   # SQLAlchemy ORM models
│   │   └── pet.py                # Pet model with typed attributes
│   ├── repositories/             # Repository pattern for data access
│   │   ├── base.py               # Generic base repository
│   │   └── pet.py                # Pet-specific repository methods
│   ├── schemas/                  # Pydantic validation schemas
│   │   └── pet.py                # Pet request/response schemas
│   ├── templates/                # Jinja2 templates
│   │   └── pet_report.j2         # Formatted report template
│   ├── worker/                   # Background workers
│   │   ├── change_detector.py    # Real-time DB change detection
│   │   └── report_generator.py   # Periodic report generation
│   └── main.py                   # FastAPI application entry point
├── tests/                        # Comprehensive test suite (94.79% coverage)
│   ├── conftest.py               # Pytest fixtures and configuration
│   ├── test_api_pets.py          # API endpoint tests
│   ├── test_change_detector.py   # Change detection tests
│   ├── test_pet_repository.py    # Repository pattern tests
│   └── ...                       # Additional test modules
├── .github/workflows/            # CI/CD pipelines
│   ├── test.yml                  # Automated testing workflow
│   ├── build.yml                 # Docker build verification
│   └── quality.yml               # Code quality checks
├── alembic/                      # Database migrations with Alembic
├── docker-compose.yml            # Production orchestration
├── docker-compose.development.yml # Development with hot-reload & Adminer
├── Dockerfile                    # Multi-stage production build
├── pyproject.toml                # Project metadata and tool configuration
├── requirements.txt              # Auto-generated production dependencies
├── requirements-dev.txt          # Auto-generated dev dependencies
├── dev.sh                        # Development helper CLI
└── test_api.sh                   # API testing script
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed on your system
- Port 8000 (API) and 5432 (PostgreSQL) available

### Running the Application

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd pet-directory
   ```

2. **Start all services with a single command:**
   ```bash
   docker-compose up
   ```

   Or for development mode with hot-reloading and Adminer:
   ```bash
   docker-compose -f docker-compose.development.yml up
   ```

3. **Services will be available at:**
   - API: http://localhost:8000
   - API Documentation (Swagger): http://localhost:8000/docs
   - API Documentation (ReDoc): http://localhost:8000/redoc
   - Adminer (dev mode only): http://localhost:8080

### Using the Development Helper

A convenient development script is provided with command-line interface:

```bash
./dev.sh [command]
```

Available commands:
- `up` - Start development environment
- `down` - Stop development environment
- `logs` - Show logs from all services
- `rebuild` - Rebuild and restart development environment
- `test` - Run test script to populate sample data
- `clean` - Remove all containers and volumes
- `worker` - Follow worker logs
- `api` - Follow API logs
- `db-shell` - Connect to PostgreSQL shell
- `status` - Show status of all services
- `help` - Show help message

## API Usage

### Example API Interactions

1. **Create a pet:**
   ```bash
   curl -X POST "http://localhost:8000/api/pets/" \
        -H "Content-Type: application/json" \
        -d '{"name": "Buddy", "pet_type": "dog"}'
   ```

2. **List all pets:**
   ```bash
   curl "http://localhost:8000/api/pets/"
   ```

3. **Get a specific pet:**
   ```bash
   curl "http://localhost:8000/api/pets/1"
   ```

4. **Update a pet:**
   ```bash
   curl -X PUT "http://localhost:8000/api/pets/1" \
        -H "Content-Type: application/json" \
        -d '{"name": "Buddy Jr."}'
   ```

5. **Delete a pet:**
   ```bash
   curl -X DELETE "http://localhost:8000/api/pets/1"
   ```

### Testing the API

Run the provided test script to populate sample data and test all endpoints:

```bash
./test_api.sh
```

This script will:
- Create 5 sample pets (2 dogs, 2 cats, 1 bird)
- Test all CRUD operations
- Update one pet's name
- Delete one of the created pets using its actual ID
- Demonstrate pagination
- Test error handling with non-existent pet ID

## Background Worker & Real-Time Change Detection

The application includes **two** worker modes for report generation:

### 1. Real-Time Change Detection Worker (Default - Recommended)

Uses PostgreSQL LISTEN/NOTIFY for instant, event-driven reporting:

- **Real-Time**: Listens for database changes using PostgreSQL's pub/sub mechanism
- **Efficient**: Only generates reports when data actually changes (INSERT, UPDATE, DELETE)
- **Instant**: Sub-second latency from change to report generation
- **Smart**: Logs detailed change information with operation type and affected records
- **Statistics**: Tracks total events, inserts, updates, deletes, and uptime

The change detector automatically:
1. Establishes a PostgreSQL LISTEN connection on the `pet_changes` channel
2. Receives notifications when pets table is modified (via database triggers)
3. Generates and prints a formatted report immediately
4. Logs detailed change information (operation type, record ID, timestamp)

**View change detector output:**
```bash
docker-compose logs -f worker
# Or using the dev script:
./dev.sh worker
```

**Example change detection log:**
```
📊 Database Change Detected:
  Operation: INSERT
  Table: pets
  Timestamp: 2025-10-31 12:30:45 UTC
  Record ID: 42
🆕 New pet added: Buddy (dog)
```

### 2. Periodic Report Generator (Legacy)

Alternative timer-based worker that generates reports every 60 seconds:

- Queries the database on a fixed schedule
- Useful for guaranteed periodic snapshots
- Can run alongside the change detector

**To use the periodic worker instead:**
```yaml
# In docker-compose.yml, change the worker command to:
command: python -m app.worker.report_generator
```

### Report Features

Both workers generate the same comprehensive report format:
- Groups pets by type with counts
- Shows summary statistics (total pets, types)
- Displays detailed pet list with emoji indicators
- Formatted timestamps and ASCII art borders
- Handles empty database gracefully

View worker output:
```bash
docker-compose logs -f worker
# Or using the dev script:
./dev.sh worker
```

Sample report format:
```
╔════════════════════════════════════════════════════════════════╗
║                    PET DIRECTORY REPORT                        ║
║                 Generated: 2025-10-30 21:32:30 UTC             ║
╚════════════════════════════════════════════════════════════════╝

📊 SUMMARY
-----------
Total Pets: 14

📈 PETS BY TYPE
---------------
  • Bird: 2 pet(s)
  • Cat: 6 pet(s)
  • Dog: 6 pet(s)

📋 DETAILED PET LIST
--------------------
1. Tweety
   Type: Bird
   ID: #8
   Registered: 2025-10-30 21:28
...
```

## Database Access

### Development Mode
When running in development mode, Adminer is available at http://localhost:8080

Connection details:
- System: PostgreSQL
- Server: db
- Username: pets_user
- Password: pets_password
- Database: pets_db

### Direct Database Access
```bash
./dev.sh db-shell
```

## Testing & Quality Assurance

### Test Coverage: 94.79%

The project includes a comprehensive test suite covering all major components:

```bash
# Run tests with coverage report
pytest

# Run tests with detailed output
pytest -v

# Generate HTML coverage report
pytest --cov-report=html
```

### Test Modules

- **`test_api_pets.py`**: Complete API endpoint testing (CRUD operations, pagination, filters, error handling)
- **`test_pet_repository.py`**: Repository pattern testing (search, bulk operations, filtering)
- **`test_change_detector.py`**: Real-time change detection and notification handling
- **`test_report_generator.py`**: Report generation logic and Jinja2 templating
- **`test_models.py`**: SQLAlchemy model validation
- **`test_schemas.py`**: Pydantic schema validation
- **`test_database.py`**: Database connection and session management
- **`test_config.py`**: Configuration loading and validation

### Code Quality Tools

**Type Checking (mypy):**
```bash
mypy app/
```
- Strict mode enabled
- Full type hints across the codebase
- SQLAlchemy and Pydantic plugins configured

**Linting (Ruff):**
```bash
ruff check app/ tests/
```
- Modern, fast Python linter (replaces Flake8, isort, pyupgrade)
- Configured for security, best practices, and code quality

**Formatting (Black):**
```bash
black app/ tests/
```
- Consistent code style across the project
- Line length: 88 characters
- Python 3.11+ target

## CI/CD Pipelines

The project includes three GitHub Actions workflows:

### 1. **Test Workflow** (`.github/workflows/test.yml`)

Runs on every push and pull request:
- Tests against Python 3.11 and 3.12 (matrix strategy)
- Spins up PostgreSQL 15 service container
- Runs full test suite with coverage reporting
- Uploads coverage reports to Codecov
- Archives HTML coverage reports as artifacts

### 2. **Build Workflow** (`.github/workflows/build.yml`)

Verifies Docker builds:
- Builds the production Docker image
- Tests that the container starts correctly
- Uses Docker layer caching for speed
- Validates multi-stage build process

### 3. **Quality Workflow** (`.github/workflows/quality.yml`)

Enforces code quality standards:
- **Quality Job**: Runs Ruff linting, Black formatting, mypy type checking
- **Security Job**: Runs Bandit security scanner and Safety dependency checker
- **Complexity Job**: Checks cyclomatic complexity and maintainability with Radon

## Design Choices and Reflection

### Architecture Decisions

1. **Repository Pattern**: Implemented a clean data access layer with generic base repository and specialized pet repository. This provides better testability, separation of concerns, and makes it easy to add new data access methods without modifying the API layer.

2. **Real-Time Change Detection**: Instead of inefficient polling, uses PostgreSQL LISTEN/NOTIFY for event-driven architecture. This reduces database load, provides instant feedback, and scales better than timer-based approaches.

3. **Async Everything**: Full async implementation from database to API handlers enables efficient concurrent request handling and better resource utilization.

4. **Type Safety First**: Comprehensive type hints with mypy strict mode catch errors at development time rather than runtime, improving code reliability and maintainability.

5. **Multi-Stage Docker Builds**: Separate production and development stages optimize for size and security in production while maintaining full dev tools in development.

6. **Configuration via Pydantic Settings**: Type-safe configuration with validation and support for environment variables and .env files follows 12-factor app methodology.

### Key Technical Innovations

**PostgreSQL Database Triggers for Change Tracking:**
```sql
-- Automatic trigger on pets table sends notifications
CREATE TRIGGER pet_changes_trigger
AFTER INSERT OR UPDATE OR DELETE ON pets
FOR EACH ROW EXECUTE FUNCTION notify_pet_changes();
```
This enables the real-time change detection worker without application-level polling.

**Generic Repository Pattern:**
```python
class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic base repository with common CRUD operations"""
```
Provides type-safe, reusable data access patterns across all models.

### Challenges Overcome

1. **Async Context Management**: Properly managing async database sessions across API and workers required careful design of context managers and dependency injection.

2. **Test Coverage for Async Code**: Achieving 94.79% coverage required mastering pytest-asyncio, mock async contexts, and testing PostgreSQL notifications.

3. **Type Safety with SQLAlchemy 2.0**: Integrating mypy with SQLAlchemy's new typing system required proper configuration and understanding of mapped columns.

4. **CI/CD with Service Containers**: GitHub Actions workflows needed proper health checks and service orchestration for PostgreSQL containers.

### Production Readiness Improvements Implemented

✅ **Comprehensive Testing**: 94.79% test coverage with pytest
✅ **Configuration Management**: Pydantic Settings with environment support
✅ **Type Safety**: Full mypy type checking with strict mode
✅ **Code Quality**: Automated linting (Ruff), formatting (Black)
✅ **Security Scanning**: Bandit for code, Safety for dependencies
✅ **CI/CD Pipelines**: Automated testing, building, and quality checks
✅ **Repository Pattern**: Clean data access layer
✅ **Health Checks**: Docker health checks for all services
✅ **Structured Logging**: Proper log levels and formatting

### Future Enhancements

With additional time, I would add:

1. **Authentication/Authorization**: JWT-based auth with role-based access control (OAuth2/OIDC)
2. **API Rate Limiting**: Protect against abuse with token bucket or sliding window algorithm
3. **Caching Layer**: Redis for frequently accessed data and pub/sub for multi-instance deployments
4. **Monitoring/Observability**: Prometheus metrics, OpenTelemetry tracing, structured logging with ELK stack
5. **API Versioning**: Versioned endpoints (/api/v1/, /api/v2/) for backward compatibility
6. **GraphQL Support**: Alternative GraphQL endpoint for flexible client queries
7. **Database Read Replicas**: Separate read/write connections for better scalability
8. **Message Queue**: RabbitMQ or AWS SQS for more complex worker patterns
9. **Admin Interface**: React/Vue admin dashboard for pet management
10. **WebSocket Support**: Real-time updates to connected clients using FastAPI WebSockets

## License

MIT

